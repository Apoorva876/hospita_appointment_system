from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied


def patient_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access this page.")
            return redirect('login')
        if request.user.role != 'patient':
            messages.error(request, "Access restricted: this page is reserved for patients.")
            if request.user.role == 'doctor':
                return redirect('doctor_dashboard')
            elif request.user.role == 'admin':
                return redirect('admin_dashboard')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def doctor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in with doctor credentials to access this area.")
            return redirect('login')
        if request.user.role != 'doctor':
            messages.error(request, "Access denied: you must be a registered doctor to view this page.")
            if request.user.role == 'patient':
                return redirect('patient_dashboard')
            elif request.user.role == 'admin':
                return redirect('admin_dashboard')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in as an administrator to access this area.")
            return redirect('login')
        if not (request.user.role == 'admin' or request.user.is_superuser or request.user.is_staff):
            messages.error(request, "Access denied: administrator privileges required.")
            if request.user.role == 'doctor':
                return redirect('doctor_dashboard')
            return redirect('patient_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
