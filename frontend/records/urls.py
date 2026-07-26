from django.urls import path
from . import views

app_name = 'records'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('students/', views.list_students, name='list_students'),
    path('add/', views.add_student, name='add_student'),
    path('search/', views.search_student, name='search_student'),
    path('student/<str:student_id>/', views.student_details, name='student_details'),
    path('update/<str:student_id>/', views.update_student, name='update_student'),
    path('delete/<str:student_id>/', views.delete_student, name='delete_student'),
    path('results/', views.result_summary, name='result_summary'),
    path('export/', views.export_results, name='export_results'),
]
