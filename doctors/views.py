from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Doctor, Department


def doctor_list_view(request):
    departments = Department.objects.all()
    selected_dept = request.GET.get('department')
    query = request.GET.get('q')

    doctors = Doctor.objects.select_related('user', 'department').all()

    if selected_dept:
        doctors = doctors.filter(department__id=selected_dept)
    if query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(specialization__icontains=query) |
            Q(department__name__icontains=query)
        )

    context = {
        'doctors': doctors,
        'departments': departments,
        'selected_dept': int(selected_dept) if selected_dept and selected_dept.isdigit() else '',
        'query': query or '',
    }
    return render(request, 'doctors/doctor_list.html', context)


def doctor_detail_view(request, doctor_id):
    doctor = get_object_or_404(Doctor.objects.select_related('user', 'department'), id=doctor_id)
    return render(request, 'doctors/doctor_detail.html', {'doctor': doctor})
