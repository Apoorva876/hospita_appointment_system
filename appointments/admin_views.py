from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone

from accounts.models import User, PatientProfile
from accounts.decorators import admin_required
from doctors.models import Department, Doctor
from doctors.forms import DepartmentForm, AdminDoctorCreateForm, AdminDoctorEditForm
from .models import Appointment


@admin_required
def admin_dashboard_view(request):
    total_doctors = Doctor.objects.count()
    total_patients = User.objects.filter(role='patient').count()
    total_departments = Department.objects.count()
    total_appointments = Appointment.objects.count()

    pending_count = Appointment.objects.filter(status='Pending').count()
    confirmed_count = Appointment.objects.filter(status='Confirmed').count()
    completed_count = Appointment.objects.filter(status='Completed').count()
    cancelled_count = Appointment.objects.filter(status__in=['Cancelled', 'Rejected']).count()

    recent_appointments = Appointment.objects.select_related('patient', 'doctor', 'doctor__user', 'doctor__department').order_by('-created_at')[:8]
    departments = Department.objects.annotate(doctor_count=Count('doctors'))[:6]
    doctors = Doctor.objects.select_related('user', 'department')[:6]

    context = {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_departments': total_departments,
        'total_appointments': total_appointments,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'recent_appointments': recent_appointments,
        'departments': departments,
        'doctors': doctors,
    }
    return render(request, 'appointments/admin_dashboard.html', context)


# --- Department Management ---
@admin_required
def admin_department_list_view(request):
    departments = Department.objects.annotate(doctor_count=Count('doctors')).order_by('name')
    return render(request, 'appointments/admin/department_list.html', {'departments': departments})


@admin_required
def admin_department_create_view(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save()
            messages.success(request, f"Department '{dept.name}' created successfully!")
            return redirect('admin_department_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DepartmentForm()
    return render(request, 'appointments/admin/department_form.html', {'form': form, 'title': 'Add New Clinical Department'})


@admin_required
def admin_department_edit_view(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            dept = form.save()
            messages.success(request, f"Department '{dept.name}' updated successfully!")
            return redirect('admin_department_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'appointments/admin/department_form.html', {
        'form': form,
        'department': department,
        'title': f'Edit Department: {department.name}'
    })


@admin_required
def admin_department_delete_view(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    if request.method == 'POST':
        name = department.name
        department.delete()
        messages.success(request, f"Department '{name}' has been deleted.")
        return redirect('admin_department_list')
    return render(request, 'appointments/admin/confirm_delete.html', {
        'object_name': f"Department '{department.name}'",
        'warning_text': f"Deleting this department will detach any doctors currently assigned to {department.name}.",
        'cancel_url': 'admin_department_list'
    })


# --- Doctor Management ---
@admin_required
def admin_doctor_list_view(request):
    doctors = Doctor.objects.select_related('user', 'department').order_by('user__first_name')
    query = request.GET.get('q')
    dept_id = request.GET.get('department')

    if query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(specialization__icontains=query) |
            Q(user__username__icontains=query)
        )
    if dept_id and dept_id.isdigit():
        doctors = doctors.filter(department_id=dept_id)

    departments = Department.objects.all()
    context = {
        'doctors': doctors,
        'departments': departments,
        'query': query or '',
        'selected_dept': int(dept_id) if dept_id and dept_id.isdigit() else '',
    }
    return render(request, 'appointments/admin/doctor_list.html', context)


@admin_required
def admin_doctor_create_view(request):
    if request.method == 'POST':
        form = AdminDoctorCreateForm(request.POST)
        if form.is_valid():
            doctor = form.save()
            messages.success(request, f"Doctor Dr. {doctor.user.get_full_name() or doctor.user.username} enrolled successfully!")
            return redirect('admin_doctor_list')
        else:
            messages.error(request, "Please correct the errors in the doctor enrollment form.")
    else:
        form = AdminDoctorCreateForm()
    return render(request, 'appointments/admin/doctor_form.html', {'form': form, 'title': 'Enroll New Specialist Doctor'})


@admin_required
def admin_doctor_edit_view(request, doctor_id):
    doctor = get_object_or_404(Doctor.objects.select_related('user'), id=doctor_id)
    if request.method == 'POST':
        form = AdminDoctorEditForm(request.POST, instance=doctor)
        if form.is_valid():
            doctor = form.save()
            messages.success(request, f"Dr. {doctor.user.get_full_name() or doctor.user.username}'s profile updated successfully!")
            return redirect('admin_doctor_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AdminDoctorEditForm(instance=doctor)
    return render(request, 'appointments/admin/doctor_form.html', {
        'form': form,
        'doctor': doctor,
        'title': f'Edit Doctor: Dr. {doctor.user.get_full_name() or doctor.user.username}'
    })


@admin_required
def admin_doctor_delete_view(request, doctor_id):
    doctor = get_object_or_404(Doctor.objects.select_related('user'), id=doctor_id)
    if request.method == 'POST':
        name = doctor.user.get_full_name() or doctor.user.username
        user = doctor.user
        doctor.delete()
        user.delete()
        messages.success(request, f"Doctor Dr. {name} and linked user account have been removed.")
        return redirect('admin_doctor_list')
    return render(request, 'appointments/admin/confirm_delete.html', {
        'object_name': f"Dr. {doctor.user.get_full_name() or doctor.user.username}",
        'warning_text': "This will remove the doctor's record and linked user account.",
        'cancel_url': 'admin_doctor_list'
    })


# --- Patient Management ---
@admin_required
def admin_patient_list_view(request):
    patients = User.objects.filter(role='patient').select_related('patient_profile').annotate(appointment_count=Count('appointments')).order_by('-date_joined')
    query = request.GET.get('q')

    if query:
        patients = patients.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )

    context = {
        'patients': patients,
        'query': query or '',
        'total_patients': patients.count()
    }
    return render(request, 'appointments/admin/patient_list.html', context)


# --- All Appointments Management ---
@admin_required
def admin_appointment_list_view(request):
    appointments = Appointment.objects.select_related('patient', 'doctor', 'doctor__user', 'doctor__department').order_by('-date', '-time')

    status_filter = request.GET.get('status')
    doctor_filter = request.GET.get('doctor')
    query = request.GET.get('q')

    if status_filter:
        appointments = appointments.filter(status=status_filter)
    if doctor_filter and doctor_filter.isdigit():
        appointments = appointments.filter(doctor_id=doctor_filter)
    if query:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=query) |
            Q(patient__last_name__icontains=query) |
            Q(patient__username__icontains=query) |
            Q(doctor__user__first_name__icontains=query) |
            Q(doctor__user__last_name__icontains=query) |
            Q(reason__icontains=query)
        )

    doctors = Doctor.objects.select_related('user').all()
    context = {
        'appointments': appointments,
        'doctors': doctors,
        'status_filter': status_filter or '',
        'doctor_filter': int(doctor_filter) if doctor_filter and doctor_filter.isdigit() else '',
        'query': query or '',
        'total_filtered': appointments.count(),
        'status_choices': ['Pending', 'Confirmed', 'Completed', 'Cancelled', 'Rejected']
    }
    return render(request, 'appointments/admin/appointment_list.html', context)


@admin_required
def admin_appointment_update_status_view(request, appointment_id, action):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    valid_actions = {
        'confirm': 'Confirmed',
        'reject': 'Rejected',
        'complete': 'Completed',
        'cancel': 'Cancelled',
    }

    if action not in valid_actions:
        messages.error(request, "Invalid status update requested.")
        return redirect('admin_appointment_list')

    new_status = valid_actions[action]
    appointment.status = new_status
    if action == 'cancel':
        appointment.doctor_notes = f"(Cancelled by Administrator on {timezone.localdate().strftime('%b %d, %Y')})"
    appointment.save()
    messages.success(request, f"Appointment #{appointment.id} updated to '{new_status}' successfully.")
    return redirect('admin_appointment_list')
