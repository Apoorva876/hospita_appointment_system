from django.db import models
from django.conf import settings


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fa-stethoscope', help_text="FontAwesome or Lucide icon name")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctors')
    specialization = models.CharField(max_length=120)
    experience = models.PositiveIntegerField(default=0, help_text="Years of professional experience")
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    working_hours_start = models.TimeField(default="09:00:00")
    working_hours_end = models.TimeField(default="17:00:00")
    bio = models.TextField(blank=True)
    room_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        dept = self.department.name if self.department else "General"
        return f"Dr. {self.user.get_full_name() or self.user.username} ({dept})"
