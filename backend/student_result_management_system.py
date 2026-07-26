import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STUDENT_RESULTS_PATH = os.path.join(BASE_DIR, "student_results.txt")
CLASS_REPORT_PATH = os.path.join(BASE_DIR, "class_report.txt")

students = [
    {
        "id": "S001",
        "name": "Anuj",
        "marks": [85, 90, 88, 92, 80],
        "total": 435,
        "percentage": 87.0,
        "grade": "A"
    },
    {
        "id": "S002",
        "name": "Anmol",
        "marks": [92, 91, 98,90, 95],
        "total": 476,
        "percentage": 95.2,
        "grade": "A+"
    },
    {
        "id": "S003",
        "name": "Kashish",
        "marks": [95, 91, 94, 96, 92],
        "total": 468,
        "percentage": 93.6,
        "grade": "A+"
    },
    {
        "id": "S004",
        "name": "Mayank",
        "marks": [68, 72, 70, 65, 74],
        "total": 349,
        "percentage": 69.8,
        "grade": "C"
    },
    {
        "id": "S005",
        "name": "Aditya",
        "marks": [88, 84, 86, 89, 90],
        "total": 437,
        "percentage": 87.4,
        "grade": "A"
    }
]

student_id = 6

def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def show_banner():
    print("=" * 60)
    print("      STUDENT RESULT MANAGEMENT SYSTEM")
    print("=" * 60)

def press_enter():
    input("\nPress Enter to Continue...")

def calculate_grade(percentage):

    if percentage >= 90:
        return "A+"

    elif percentage >= 80:
        return "A"

    elif percentage >= 70:
        return "B"

    elif percentage >= 60:
        return "C"

    elif percentage >= 50:
        return "D"

    else:
        return "F"

def calculate_result(marks):

    total = sum(marks)

    percentage = total / len(marks)

    grade = calculate_grade(percentage)

    return total, percentage, grade

def add_student():

    global student_id

    print("\n===== ADD STUDENT =====")

    name = input("Enter Student Name : ")

    marks = []

    for i in range(1, 6):

        while True:

            try:

                mark = float(input(f"Enter Subject {i} Marks : "))

                if 0 <= mark <= 100:
                    marks.append(mark)
                    break

                else:
                    print("Marks should be between 0 and 100.")

            except ValueError:
                print("Invalid Input! Enter numbers only.")

    total, percentage, grade = calculate_result(marks)

    student = {

        "id": f"S{student_id:03}",

        "name": name,

        "marks": marks,

        "total": total,

        "percentage": percentage,

        "grade": grade

    }

    students.append(student)

    print("\nStudent Added Successfully!")

    print("Student ID :", student["id"])

    student_id += 1

def display_students():

    print("\n===== STUDENT RECORDS =====")

    if len(students) == 0:
        print("No Student Records Found.")
        return

    print("-" * 90)

    print(f"{'ID':<10}{'NAME':<20}{'TOTAL':<10}{'PERCENT':<12}{'GRADE':<10}")

    print("-" * 90)

    for student in students:

        display_name = student['name'][:20]
        print(f"{student['id']:<10}"
              f"{display_name:<20}"
              f"{student['total']:<10}"
              f"{student['percentage']:<12.2f}"
              f"{student['grade']:<10}")

    print("-" * 90)

def search_student():

    print("\n===== SEARCH STUDENT =====")

    key = input("Enter Student ID or Name : ").lower()

    for student in students:

        if (student["id"].lower() == key or
                key in student["name"].lower()):

            print("\nStudent Found\n")

            print("Student ID :", student["id"])
            print("Name       :", student["name"])
            print("Marks      :", student["marks"])
            print("Total      :", student["total"])
            print("Percentage :", round(student["percentage"], 2))
            print("Grade      :", student["grade"])

            return student

    print("Student Not Found.")

    return None

def update_student():

    print("\n===== UPDATE STUDENT =====")

    student = search_student()

    if student is None:
        return

    # ---------- Update Name ----------
    print(f"\nCurrent Name : {student['name']}")
    new_name = input("Enter New Name (Press Enter to keep same): ")

    if new_name.strip() != "":
        student["name"] = new_name

    # ---------- Update Marks ----------
    print("\nEnter New Marks")

    marks = []

    for i in range(1, 6):
        while True:
            try:
                mark = float(input(f"Subject {i}: "))
                if 0 <= mark <= 100:
                    marks.append(mark)
                    break
                else:
                    print("Marks should be between 0 and 100.")
            except ValueError:
                print("Invalid input!")

    student["marks"] = marks

    total, percentage, grade = calculate_result(marks)
    student["total"] = total
    student["percentage"] = percentage
    student["grade"] = grade

    print("\n✅ Student Updated Successfully!")

def save_result():

    if len(students) == 0:
        print("\nNo Records Available.")
        return

    with open(STUDENT_RESULTS_PATH, "w") as file:

        for student in students:

            marks = ",".join(map(str, student["marks"]))

            file.write(
                f"{student['id']}|"
                f"{student['name']}|"
                f"{marks}|"
                f"{student['total']}|"
                f"{student['percentage']}|"
                f"{student['grade']}\n"
            )

    print("\nResults Saved Successfully!")

def load_result():

    global students
    global student_id

    students.clear()

    try:

        with open(STUDENT_RESULTS_PATH, "r") as file:

            for line in file:

                line_content = line.strip()
                if not line_content:
                    continue

                data = line_content.split("|")
                if len(data) < 6:
                    continue

                try:
                    student = {

                        "id": data[0],

                        "name": data[1],

                        "marks": list(map(float, data[2].split(","))),

                        "total": float(data[3]),

                        "percentage": float(data[4]),

                        "grade": data[5]

                    }

                    students.append(student)
                except ValueError:
                    continue

        if len(students) > 0:

            student_id = int(students[-1]["id"][1:]) + 1

        print("\nRecords Loaded Successfully!")

    except FileNotFoundError:

        print(f"\n{STUDENT_RESULTS_PATH} File Not Found.")

def export_result():

    if len(students) == 0:

        print("\nNo Records Available.")
        return

    with open(CLASS_REPORT_PATH, "w") as report:

        report.write("=" * 70 + "\n")
        report.write("           CLASS RESULT REPORT\n")
        report.write("=" * 70 + "\n\n")

        for student in students:

            report.write(f"Student ID : {student['id']}\n")
            report.write(f"Name       : {student['name']}\n")
            report.write(f"Marks      : {student['marks']}\n")
            report.write(f"Total      : {student['total']}\n")
            report.write(f"Percentage : {student['percentage']:.2f}%\n")
            report.write(f"Grade      : {student['grade']}\n")
            report.write("-" * 70 + "\n")

    print("\nClass Report Exported Successfully!")

def result_menu():

    while True:

        clear_screen()

        print("=" * 50)
        print("           RESULT MENU")
        print("=" * 50)

        print("1. Save Result")
        print("2. Load Result")
        print("3. Export Result")
        print("4. Back to Main Menu")

        choice = input("\nEnter Choice : ")

        if choice == "1":

            save_result()

        elif choice == "2":

            load_result()

        elif choice == "3":

            export_result()

        elif choice == "4":

            break

        else:

            print("\nInvalid Choice!")

        press_enter()

def main():

    while True:

        clear_screen()

        show_banner()

        print("1. Add Student")
        print("2. Display Students")
        print("3. Search Student")
        print("4. Update Student")
        print("5. Result")
        print("99. Exit")

        choice = input("\nEnter Choice : ")

        if choice == "1":

            add_student()

        elif choice == "2":
            
            display_students()

        elif choice == "3":

            search_student()

        elif choice == "4":

            update_student()

        elif choice == "5":

            result_menu()

        elif choice == "99":

            print("\nThank You!")
            break

        else:

            print("\nInvalid Choice!")

        press_enter()

if __name__ == "__main__":
    main()