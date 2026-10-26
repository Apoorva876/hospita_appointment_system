from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.db import transaction

from .forms import (
    PatientRegistrationForm,
    UserUpdateForm,
    PatientProfileUpdateForm,
    DoctorProfileUpdateForm,
)
from .models import PatientProfile
from doctors.models import Doctor


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Welcome to MediCare, {user.first_name or user.username}! Your patient account was created successfully.")
            login(request, user)
            return redirect('patient_dashboard')
        else:
            messages.error(request, "Please correct the errors in the registration form below.")
    else:
        form = PatientRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")

            # Next parameter handling or role-based landing
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)

            return redirect('dashboard_redirect')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out securely.")
    return redirect('login')


@login_required
def dashboard_redirect_view(request):
    """Directs user to their appropriate role-specific dashboard."""
    if request.user.role == 'doctor':
        return redirect('doctor_dashboard')
    elif request.user.role == 'admin' or request.user.is_superuser or request.user.is_staff:
        return redirect('admin_dashboard')
    else:
        return redirect('patient_dashboard')


@login_required
def profile_view(request):
    user = request.user
    patient_profile = None
    doctor_profile = None

    if user.role == 'patient':
        patient_profile, _ = PatientProfile.objects.get_or_create(user=user)
    elif user.role == 'doctor':
        doctor_profile = Doctor.objects.filter(user=user).first()

    context = {
        'profile_user': user,
        'patient_profile': patient_profile,
        'doctor_profile': doctor_profile,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit_view(request):
    user = request.user
    patient_profile = None
    doctor_profile = None
    patient_form = None
    doctor_form = None

    if user.role == 'patient':
        patient_profile, _ = PatientProfile.objects.get_or_create(user=user)
    elif user.role == 'doctor':
        doctor_profile = Doctor.objects.filter(user=user).first()

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)

        if user.role == 'patient':
            patient_form = PatientProfileUpdateForm(request.POST, instance=patient_profile)
            if user_form.is_valid() and patient_form.is_valid():
                with transaction.atomic():
                    user_form.save()
                    patient_form.save()
                messages.success(request, "Your patient profile has been updated successfully!")
                return redirect('profile')
            else:
                messages.error(request, "Please fix the errors below before submitting.")
        elif user.role == 'doctor' and doctor_profile:
            doctor_form = DoctorProfileUpdateForm(request.POST, instance=doctor_profile)
            if user_form.is_valid() and doctor_form.is_valid():
                with transaction.atomic():
                    user_form.save()
                    doctor_form.save()
                messages.success(request, "Your doctor profile has been updated successfully!")
                return redirect('profile')
            else:
                messages.error(request, "Please fix the errors below before submitting.")
        else:
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Your administrator profile has been updated successfully!")
                return redirect('profile')
            else:
                messages.error(request, "Please fix the errors below.")
    else:
        user_form = UserUpdateForm(instance=user)
        if user.role == 'patient':
            patient_form = PatientProfileUpdateForm(instance=patient_profile)
        elif user.role == 'doctor' and doctor_profile:
            doctor_form = DoctorProfileUpdateForm(instance=doctor_profile)

    context = {
        'user_form': user_form,
        'patient_form': patient_form,
        'doctor_form': doctor_form,
        'patient_profile': patient_profile,
        'doctor_profile': doctor_profile,
    }
    return render(request, 'accounts/profile_edit.html', context)


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was changed successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the password errors below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})
