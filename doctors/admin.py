from django.contrib import admin
from .models import Department, Doctor


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'specialization', 'experience', 'fee', 'working_hours_start', 'working_hours_end')
    list_filter = ('department', 'specialization')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'specialization')
