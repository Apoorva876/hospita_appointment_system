from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PatientProfile


class PatientProfileInline(admin.StackedInline):
    model = PatientProfile
    can_delete = False
    verbose_name_plural = 'Patient Profile'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (PatientProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Contact', {'fields': ('role', 'phone')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role & Contact', {'fields': ('role', 'phone', 'email')}),
    )


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'blood_group', 'date_of_birth', 'emergency_contact')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'emergency_contact')
    list_filter = ('gender', 'blood_group')
