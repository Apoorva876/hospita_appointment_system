from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, date

from .models import Appointment
from doctors.models import Doctor, Department
from accounts.models import User
from accounts.decorators import patient_required, doctor_required, admin_required


def home_view(request):
    departments = Department.objects.all()[:6]
    featured_doctors = Doctor.objects.select_related('user', 'department').all()[:4]
    total_doctors = Doctor.objects.count()
    total_patients = User.objects.filter(role='patient').count()
    total_departments = Department.objects.count()

    context = {
        'departments': departments,
        'featured_doctors': featured_doctors,
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_departments': total_departments,
    }
    return render(request, 'home.html', context)


@patient_required
def patient_dashboard_view(request):
    appointments = Appointment.objects.filter(patient=request.user).select_related('doctor', 'doctor__department', 'doctor__user').order_by('-date', '-time')

    today = timezone.localdate()
    upcoming = appointments.filter(date__gte=today, status__in=['Pending', 'Confirmed'])
    past = appointments.exclude(id__in=upcoming.values_list('id', flat=True))

    context = {
        'upcoming_appointments': upcoming,
        'past_appointments': past,
        'total_count': appointments.count(),
        'pending_count': appointments.filter(status='Pending').count(),
        'confirmed_count': appointments.filter(status='Confirmed').count(),
    }
    return render(request, 'appointments/patient_dashboard.html', context)


@doctor_required
def doctor_dashboard_view(request):
    doctor = get_object_or_404(Doctor.objects.select_related('department'), user=request.user)
    today = timezone.localdate()

    all_appointments = Appointment.objects.filter(doctor=doctor).select_related('patient', 'patient__patient_profile').order_by('date', 'time')
    today_appointments = all_appointments.filter(date=today).exclude(status__in=['Cancelled', 'Rejected'])
    pending_appointments = all_appointments.filter(status='Pending')
    confirmed_appointments = all_appointments.filter(status='Confirmed')
    completed_appointments = all_appointments.filter(status='Completed')

    # Optional search / filter within doctor's appointments
    query = request.GET.get('q', '').strip()
    date_filter = request.GET.get('date')

    search_results = None
    if query or date_filter:
        search_results = all_appointments
        if query:
            search_results = search_results.filter(
                Q(patient__first_name__icontains=query) |
                Q(patient__last_name__icontains=query) |
                Q(patient__username__icontains=query) |
                Q(reason__icontains=query) |
                Q(doctor_notes__icontains=query)
            )
        if date_filter:
            search_results = search_results.filter(date=date_filter)

    context = {
        'doctor': doctor,
        'today': today,
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'confirmed_appointments': confirmed_appointments,
        'completed_appointments': completed_appointments,
        'search_results': search_results,
        'query': query,
        'date_filter': date_filter or '',
        'total_count': all_appointments.count(),
        'today_count': today_appointments.count(),
        'pending_count': pending_appointments.count(),
        'completed_count': completed_appointments.count(),
    }
    return render(request, 'appointments/doctor_dashboard.html', context)


from .admin_views import (
    admin_dashboard_view,
    admin_department_list_view,
    admin_department_create_view,
    admin_department_edit_view,
    admin_department_delete_view,
    admin_doctor_list_view,
    admin_doctor_create_view,
    admin_doctor_edit_view,
    admin_doctor_delete_view,
    admin_patient_list_view,
    admin_appointment_list_view,
    admin_appointment_update_status_view,
)



@patient_required
def book_appointment_view(request, doctor_id):
    doctor = get_object_or_404(Doctor.objects.select_related('user', 'department'), id=doctor_id)
    today = timezone.localdate()

    if request.method == 'POST':
        app_date_str = request.POST.get('date')
        app_time_str = request.POST.get('time')
        reason = request.POST.get('reason', '').strip()

        if not app_date_str or not app_time_str or not reason:
            messages.error(request, "Please fill in all required fields (date, time, and reason).")
            return render(request, 'appointments/book.html', {'doctor': doctor, 'today': today})

        try:
            app_date = datetime.strptime(app_date_str, '%Y-%m-%d').date()
            app_time = datetime.strptime(app_time_str, '%H:%M').time()
        except ValueError:
            messages.error(request, "Invalid date or time format provided.")
            return render(request, 'appointments/book.html', {'doctor': doctor, 'today': today})

        # Rule 1: Past dates rejected
        if app_date < today:
            messages.error(request, "Appointments cannot be booked for past dates.")
            return render(request, 'appointments/book.html', {'doctor': doctor, 'today': today})

        # Rule 2: Working hours validation
        if app_time < doctor.working_hours_start or app_time > doctor.working_hours_end:
            messages.error(
                request,
                f"Selected time is outside Dr. {doctor.user.get_full_name() or doctor.user.username}'s working hours ({doctor.working_hours_start.strftime('%I:%M %p')} - {doctor.working_hours_end.strftime('%I:%M %p')})."
            )
            return render(request, 'appointments/book.html', {'doctor': doctor, 'today': today})

        # Rule 3: No double booking
        conflict_exists = Appointment.objects.filter(
            doctor=doctor,
            date=app_date,
            time=app_time,
            status__in=['Pending', 'Confirmed']
        ).exists()

        if conflict_exists:
            messages.error(request, f"This time slot ({app_time.strftime('%I:%M %p')} on {app_date}) is already booked. Please choose another slot.")
            return render(request, 'appointments/book.html', {'doctor': doctor, 'today': today})

        # Create appointment
        Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            date=app_date,
            time=app_time,
            reason=reason,
            status='Pending'
        )
        messages.success(request, f"Your appointment request with Dr. {doctor.user.get_full_name() or doctor.user.username} has been submitted successfully!")
        return redirect('patient_dashboard')

    return render(request, 'appointments/book.html', {'doctor': doctor, 'today': today})


@patient_required
def cancel_appointment_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Rule: Only owning patient can cancel
    if appointment.patient != request.user:
        messages.error(request, "You are not authorized to cancel this appointment.")
        return redirect('patient_dashboard')

    # Rule: Completed or already rejected/cancelled cannot be cancelled
    if appointment.status == 'Completed':
        messages.error(request, "Completed appointments cannot be cancelled.")
        return redirect('patient_dashboard')

    if appointment.status in ['Cancelled', 'Rejected']:
        messages.warning(request, f"This appointment is already {appointment.status.lower()}.")
        return redirect('patient_dashboard')

    if request.method == 'POST':
        appointment.status = 'Cancelled'
        appointment.save()
        messages.success(request, f"Appointment #{appointment.id} has been cancelled.")
        return redirect('patient_dashboard')

    return render(request, 'appointments/cancel_confirm.html', {'appointment': appointment})


@doctor_required
def update_appointment_status_view(request, appointment_id, action):
    doctor = get_object_or_404(Doctor, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Rule: Only assigned doctor can confirm, reject or complete
    if appointment.doctor != doctor:
        messages.error(request, "You are not the assigned doctor for this appointment.")
        return redirect('doctor_dashboard')

    valid_actions = {
        'confirm': 'Confirmed',
        'reject': 'Rejected',
        'complete': 'Completed'
    }

    if action not in valid_actions:
        messages.error(request, "Invalid action requested.")
        return redirect('doctor_dashboard')

    new_status = valid_actions[action]

    if request.method == 'POST':
        notes = request.POST.get('doctor_notes', '').strip()
        appointment.status = new_status
        if notes:
            appointment.doctor_notes = notes
        appointment.save()
        messages.success(request, f"Appointment #{appointment.id} updated to {new_status}.")
        return redirect('doctor_dashboard')

    return render(request, 'appointments/doctor_action_confirm.html', {
        'appointment': appointment,
        'action': action,
        'new_status': new_status
    })
