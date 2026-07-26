from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, Http404
import os
from pathlib import Path
import student_result_management_system as backend

# Ensure initial data is synced/saved if file doesn't exist
def sync_data():
    # If the database file doesn't exist, save the default initial students
    if not os.path.exists(backend.STUDENT_RESULTS_PATH):
        backend.save_result()
    backend.load_result()

def save_data():
    backend.save_result()

def dashboard(request):
    sync_data()
    total_students = len(backend.students)
    
    if total_students > 0:
        avg_percentage = sum(s['percentage'] for s in backend.students) / total_students
        top_student = max(backend.students, key=lambda s: s['percentage'])
    else:
        avg_percentage = 0.0
        top_student = None

    # Calculate grade distribution
    grade_counts = {'A+': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    pass_count = 0
    fail_count = 0
    
    for s in backend.students:
        g = s['grade']
        if g in grade_counts:
            grade_counts[g] += 1
        if g != 'F':
            pass_count += 1
        else:
            fail_count += 1

    grade_data = []
    for grade, count in grade_counts.items():
        pct = (count / total_students) * 100 if total_students > 0 else 0
        grade_data.append({
            'grade': grade,
            'count': count,
            'percentage': round(pct, 1)
        })

    context = {
        'total_students': total_students,
        'avg_percentage': round(avg_percentage, 2),
        'top_student': top_student,
        'grade_data': grade_data,
        'pass_count': pass_count,
        'fail_count': fail_count,
    }
    return render(request, 'records/dashboard.html', context)

def list_students(request):
    sync_data()
    return render(request, 'records/list_students.html', {'students': backend.students})

def add_student(request):
    sync_data()
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        marks = []
        try:
            for i in range(1, 6):
                mark_val = request.POST.get(f'subject_{i}', '')
                if mark_val == '':
                    raise ValueError(f"Subject {i} marks are required.")
                mark = float(mark_val)
                if not (0 <= mark <= 100):
                    raise ValueError("Marks should be between 0 and 100.")
                marks.append(mark)
            
            if not name:
                raise ValueError("Student name is required.")
                
            # Call calculations
            total, percentage, grade = backend.calculate_result(marks)
            
            student = {
                "id": f"S{backend.student_id:03}",
                "name": name,
                "marks": marks,
                "total": total,
                "percentage": percentage,
                "grade": grade
            }
            backend.students.append(student)
            backend.student_id += 1
            save_data()
            
            messages.success(request, f"Student {name} (ID: {student['id']}) added successfully!")
            return redirect('records:list_students')
            
        except ValueError as e:
            messages.error(request, str(e))
            # Fall through to re-render form with current data
            
    return render(request, 'records/add_student.html')

def search_student(request):
    sync_data()
    query = request.GET.get('query', '').strip().lower()
    results = []
    
    if query:
        for student in backend.students:
            if query == student['id'].lower() or query in student['name'].lower():
                results.append(student)
                
    return render(request, 'records/search_student.html', {
        'query': request.GET.get('query', ''),
        'results': results
    })

def student_details(request, student_id):
    sync_data()
    for student in backend.students:
        if student['id'].lower() == student_id.lower():
            return render(request, 'records/student_details.html', {'student': student})
    raise Http404("Student not found")

def update_student(request, student_id):
    sync_data()
    target_student = None
    for student in backend.students:
        if student['id'].lower() == student_id.lower():
            target_student = student
            break
            
    if not target_student:
        raise Http404("Student not found")
        
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        marks = []
        try:
            for i in range(1, 6):
                mark_val = request.POST.get(f'subject_{i}', '')
                if mark_val == '':
                    raise ValueError(f"Subject {i} marks are required.")
                mark = float(mark_val)
                if not (0 <= mark <= 100):
                    raise ValueError("Marks should be between 0 and 100.")
                marks.append(mark)
                
            if not name:
                raise ValueError("Student name is required.")
                
            # Update fields
            target_student['name'] = name
            target_student['marks'] = marks
            
            # Recalculate results using backend functions
            total, percentage, grade = backend.calculate_result(marks)
            target_student['total'] = total
            target_student['percentage'] = percentage
            target_student['grade'] = grade
            
            save_data()
            messages.success(request, f"Student {name} updated successfully!")
            return redirect('records:student_details', student_id=target_student['id'])
            
        except ValueError as e:
            messages.error(request, str(e))
            
    return render(request, 'records/update_student.html', {'student': target_student})

def delete_student(request, student_id):
    sync_data()
    global_students = backend.students
    student_to_delete = None
    
    for idx, student in enumerate(global_students):
        if student['id'].lower() == student_id.lower():
            student_to_delete = student
            global_students.pop(idx)
            break
            
    if student_to_delete:
        save_data()
        messages.success(request, f"Student {student_to_delete['name']} deleted successfully!")
    else:
        messages.error(request, "Student not found.")
        
    return redirect('records:list_students')

def result_summary(request):
    sync_data()
    total_students = len(backend.students)
    if total_students == 0:
        context = {
            'total_students': 0,
            'avg_percentage': 0,
            'pass_percentage': 0,
            'fail_percentage': 0,
            'grade_percentages': {},
            'highest_student': None,
            'lowest_student': None,
        }
        return render(request, 'records/result_summary.html', context)
        
    avg_percentage = sum(s['percentage'] for s in backend.students) / total_students
    highest_student = max(backend.students, key=lambda s: s['percentage'])
    lowest_student = min(backend.students, key=lambda s: s['percentage'])
    
    grade_counts = {'A+': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    pass_count = 0
    for s in backend.students:
        g = s['grade']
        if g in grade_counts:
            grade_counts[g] += 1
        if g != 'F':
            pass_count += 1
            
    pass_percentage = (pass_count / total_students) * 100
    fail_percentage = 100 - pass_percentage
    
    grade_percentages = {}
    for grade, count in grade_counts.items():
        grade_percentages[grade] = round((count / total_students) * 100, 1)
        
    context = {
        'total_students': total_students,
        'avg_percentage': round(avg_percentage, 2),
        'pass_percentage': round(pass_percentage, 1),
        'fail_percentage': round(fail_percentage, 1),
        'grade_counts': grade_counts,
        'grade_percentages': grade_percentages,
        'highest_student': highest_student,
        'lowest_student': lowest_student,
    }
    return render(request, 'records/result_summary.html', context)

def export_results(request):
    sync_data()
    if len(backend.students) == 0:
        messages.error(request, "No student records available to export.")
        return redirect('records:dashboard')
        
    backend.export_result()
    report_path = Path(backend.CLASS_REPORT_PATH)
    
    if report_path.exists():
        with open(report_path, "r") as file:
            response = HttpResponse(file.read(), content_type="text/plain")
            response['Content-Disposition'] = 'attachment; filename="class_report.txt"'
            return response
    else:
        messages.error(request, "Failed to export class report.")
        return redirect('records:dashboard')
