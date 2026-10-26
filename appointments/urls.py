from django.urls import path
from . import views

urlpatterns = [
    # Patient & Doctor Dashboards
    path('my/', views.patient_dashboard_view, name='patient_dashboard'),
    path('doctor/', views.doctor_dashboard_view, name='doctor_dashboard'),
    path('book/<int:doctor_id>/', views.book_appointment_view, name='book_appointment'),
    path('<int:appointment_id>/cancel/', views.cancel_appointment_view, name='cancel_appointment'),
    path('<int:appointment_id>/status/<str:action>/', views.update_appointment_status_view, name='update_appointment_status'),

    # Admin Portal Management Routes
    path('admin-overview/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin/departments/', views.admin_department_list_view, name='admin_department_list'),
    path('admin/departments/create/', views.admin_department_create_view, name='admin_department_create'),
    path('admin/departments/<int:department_id>/edit/', views.admin_department_edit_view, name='admin_department_edit'),
    path('admin/departments/<int:department_id>/delete/', views.admin_department_delete_view, name='admin_department_delete'),

    path('admin/doctors/', views.admin_doctor_list_view, name='admin_doctor_list'),
    path('admin/doctors/create/', views.admin_doctor_create_view, name='admin_doctor_create'),
    path('admin/doctors/<int:doctor_id>/edit/', views.admin_doctor_edit_view, name='admin_doctor_edit'),
    path('admin/doctors/<int:doctor_id>/delete/', views.admin_doctor_delete_view, name='admin_doctor_delete'),

    path('admin/patients/', views.admin_patient_list_view, name='admin_patient_list'),
    path('admin/appointments/', views.admin_appointment_list_view, name='admin_appointment_list'),
    path('admin/appointments/<int:appointment_id>/status/<str:action>/', views.admin_appointment_update_status_view, name='admin_appointment_update_status'),
]

