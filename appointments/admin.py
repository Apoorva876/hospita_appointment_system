from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'date', 'time', 'status', 'created_at')
    list_filter = ('status', 'date', 'doctor__department')
    search_fields = ('patient__username', 'patient__email', 'doctor__user__first_name', 'doctor__user__last_name', 'reason')
