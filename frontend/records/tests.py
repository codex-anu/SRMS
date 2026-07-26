from django.test import TestCase, Client
from django.urls import reverse
import os
import student_result_management_system as backend

class StudentResultSystemTests(TestCase):
    
    def setUp(self):
        # Setup clean environment for each test
        self.client = Client()
        backend.students = [
            {
                "id": "S001",
                "name": "Test Student A",
                "marks": [80, 85, 90, 80, 85],
                "total": 420,
                "percentage": 84.0,
                "grade": "A"
            },
            {
                "id": "S002",
                "name": "Test Student B",
                "marks": [50, 45, 55, 60, 50],
                "total": 260,
                "percentage": 52.0,
                "grade": "D"
            }
        ]
        backend.student_id = 3
        # Write setup data to file
        backend.save_result()

    def tearDown(self):
        # Cleanup created files
        for path in [backend.STUDENT_RESULTS_PATH, backend.CLASS_REPORT_PATH]:
            if os.path.exists(path):
                os.remove(path)

    def test_dashboard_view(self):
        response = self.client.get(reverse('records:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Student A")
        self.assertContains(response, "2") # Total students
        self.assertContains(response, "68.00%") # Average percentage (84 + 52) / 2 = 68.0

    def test_list_students_view(self):
        response = self.client.get(reverse('records:list_students'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Student A")
        self.assertContains(response, "Test Student B")
        self.assertContains(response, "S001")
        self.assertContains(response, "S002")

    def test_add_student_valid(self):
        post_data = {
            'name': 'New Student',
            'subject_1': 95,
            'subject_2': 90,
            'subject_3': 95,
            'subject_4': 100,
            'subject_5': 90,
        }
        response = self.client.post(reverse('records:add_student'), post_data)
        # Verify redirect to list view
        self.assertRedirects(response, reverse('records:list_students'))
        
        # Verify student added in list
        backend.load_result()
        self.assertEqual(len(backend.students), 3)
        self.assertEqual(backend.students[-1]['name'], 'New Student')
        self.assertEqual(backend.students[-1]['total'], 470)
        self.assertEqual(backend.students[-1]['grade'], 'A+')

    def test_add_student_invalid_marks(self):
        post_data = {
            'name': 'New Student',
            'subject_1': 105, # Invalid mark (>100)
            'subject_2': 90,
            'subject_3': 95,
            'subject_4': 100,
            'subject_5': 90,
        }
        response = self.client.post(reverse('records:add_student'), post_data)
        # Should stay on page and render message
        self.assertEqual(response.status_code, 200)
        # Verify backend list size didn't increase
        self.assertEqual(len(backend.students), 2)

    def test_search_student(self):
        # Search by full ID
        response = self.client.get(reverse('records:search_student'), {'query': 'S001'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Student A")
        
        # Search by partial name
        response = self.client.get(reverse('records:search_student'), {'query': 'student'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Student A")
        self.assertContains(response, "Test Student B")
        
        # Search no matches
        response = self.client.get(reverse('records:search_student'), {'query': 'Unknown'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Match Found")

    def test_student_details(self):
        response = self.client.get(reverse('records:student_details', args=['S001']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Student A")
        self.assertContains(response, "80.0") # Subject 1 marks

        # Non-existing student should yield 404
        response = self.client.get(reverse('records:student_details', args=['S999']))
        self.assertEqual(response.status_code, 404)

    def test_update_student_valid(self):
        post_data = {
            'name': 'Updated Name A',
            'subject_1': 90,
            'subject_2': 90,
            'subject_3': 90,
            'subject_4': 90,
            'subject_5': 90,
        }
        response = self.client.post(reverse('records:update_student', args=['S001']), post_data)
        self.assertRedirects(response, reverse('records:student_details', args=['S001']))
        
        backend.load_result()
        student = backend.students[0]
        self.assertEqual(student['name'], 'Updated Name A')
        self.assertEqual(student['total'], 450)
        self.assertEqual(student['percentage'], 90.0)
        self.assertEqual(student['grade'], 'A+')

    def test_delete_student(self):
        response = self.client.get(reverse('records:delete_student', args=['S001']))
        self.assertRedirects(response, reverse('records:list_students'))
        
        backend.load_result()
        self.assertEqual(len(backend.students), 1)
        self.assertEqual(backend.students[0]['id'], 'S002')

    def test_result_summary(self):
        response = self.client.get(reverse('records:result_summary'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pass Rate")
        self.assertContains(response, "100.0%") # Both students passed (A and D grades)

    def test_export_results(self):
        response = self.client.get(reverse('records:export_results'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertIn('attachment; filename="class_report.txt"', response['Content-Disposition'])
        self.assertTrue(os.path.exists(backend.CLASS_REPORT_PATH))
