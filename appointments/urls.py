from django.urls import path
from . import views

urlpatterns = [
    path('my/', views.patient_dashboard_view, name='patient_dashboard'),
    path('doctor/', views.doctor_dashboard_view, name='doctor_dashboard'),
    path('admin-overview/', views.admin_dashboard_view, name='admin_dashboard'),
    path('book/<int:doctor_id>/', views.book_appointment_view, name='book_appointment'),
    path('<int:appointment_id>/cancel/', views.cancel_appointment_view, name='cancel_appointment'),
    path('<int:appointment_id>/status/<str:action>/', views.update_appointment_status_view, name='update_appointment_status'),
]
