from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date, time, timedelta

from accounts.models import User, PatientProfile
from doctors.models import Department, Doctor
from appointments.models import Appointment


class HospitalSystemTests(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Departments
        self.dept_cardio = Department.objects.create(
            name="Cardiology",
            description="Heart care and diagnostics."
        )
        self.dept_neuro = Department.objects.create(
            name="Neurology",
            description="Brain and nerve care."
        )

        # 2. Doctor user and profile
        self.doc_user = User.objects.create_user(
            username="dr_smith",
            email="dr.smith@medicare.test",
            password="password123",
            first_name="Alice",
            last_name="Smith",
            role="doctor"
        )
        self.doctor = Doctor.objects.create(
            user=self.doc_user,
            department=self.dept_cardio,
            specialization="Cardiologist",
            experience=10,
            fee=100.00,
            working_hours_start=time(9, 0),
            working_hours_end=time(17, 0)
        )

        # Another doctor
        self.doc_user2 = User.objects.create_user(
            username="dr_jones",
            email="dr.jones@medicare.test",
            password="password123",
            first_name="Bob",
            last_name="Jones",
            role="doctor"
        )
        self.doctor2 = Doctor.objects.create(
            user=self.doc_user2,
            department=self.dept_neuro,
            specialization="Neurologist",
            experience=8,
            fee=120.00,
            working_hours_start=time(10, 0),
            working_hours_end=time(16, 0)
        )

        # 3. Patient user
        self.patient_user = User.objects.create_user(
            username="patient_jane",
            email="jane@example.test",
            password="password123",
            first_name="Jane",
            last_name="Doe",
            role="patient"
        )
        self.patient_profile = PatientProfile.objects.create(
            user=self.patient_user,
            gender="Female",
            blood_group="A+"
        )

        # 4. Another patient user
        self.other_patient = User.objects.create_user(
            username="patient_mark",
            email="mark@example.test",
            password="password123",
            first_name="Mark",
            last_name="Wood",
            role="patient"
        )

        # 5. Admin user
        self.admin_user = User.objects.create_user(
            username="admin_boss",
            email="admin@medicare.test",
            password="password123",
            role="admin",
            is_staff=True,
            is_superuser=True
        )

    # --- Role-Based Access Control Tests ---
    def test_patient_cannot_access_doctor_dashboard(self):
        self.client.login(username="patient_jane", password="password123")
        response = self.client.get(reverse('doctor_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('patient_dashboard'))

    def test_doctor_cannot_access_patient_dashboard(self):
        self.client.login(username="dr_smith", password="password123")
        response = self.client.get(reverse('patient_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('doctor_dashboard'))

    def test_doctor_cannot_access_admin_overview(self):
        self.client.login(username="dr_smith", password="password123")
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('doctor_dashboard'))

    def test_patient_cannot_access_admin_overview(self):
        self.client.login(username="patient_jane", password="password123")
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('patient_dashboard'))

    # --- Doctor Listing and Filter Tests ---
    def test_doctor_list_and_search(self):
        response = self.client.get(reverse('doctor_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice")
        self.assertContains(response, "Bob")

        # Search by query
        response_search = self.client.get(reverse('doctor_list') + '?q=Alice')
        self.assertContains(response_search, "Alice")
        self.assertNotContains(response_search, "dr_jones")

        # Filter by department
        response_dept = self.client.get(reverse('doctor_list') + f'?department={self.dept_neuro.id}')
        self.assertContains(response_dept, "Bob")
        self.assertNotContains(response_dept, "Alice")

    # --- Appointment Booking Logic Tests ---
    def test_booking_valid_slot(self):
        self.client.login(username="patient_jane", password="password123")
        future_date = timezone.localdate() + timedelta(days=2)
        valid_time = "10:30"

        response = self.client.post(reverse('book_appointment', args=[self.doctor.id]), {
            'date': future_date.strftime('%Y-%m-%d'),
            'time': valid_time,
            'reason': 'Regular heart health checkup'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Appointment.objects.filter(
            patient=self.patient_user,
            doctor=self.doctor,
            date=future_date,
            status='Pending'
        ).exists())

    def test_booking_rejects_past_date(self):
        self.client.login(username="patient_jane", password="password123")
        past_date = timezone.localdate() - timedelta(days=2)

        response = self.client.post(reverse('book_appointment', args=[self.doctor.id]), {
            'date': past_date.strftime('%Y-%m-%d'),
            'time': "10:00",
            'reason': 'Past date test'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Appointments cannot be booked for past dates.")
        self.assertFalse(Appointment.objects.filter(date=past_date).exists())

    def test_booking_rejects_outside_working_hours(self):
        self.client.login(username="patient_jane", password="password123")
        future_date = timezone.localdate() + timedelta(days=3)
        # Working hours start at 09:00, so 07:00 is outside
        response = self.client.post(reverse('book_appointment', args=[self.doctor.id]), {
            'date': future_date.strftime('%Y-%m-%d'),
            'time': "07:00",
            'reason': 'Early morning checkup'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "outside Dr. Alice Smith&#x27;s working hours")
        self.assertFalse(Appointment.objects.filter(date=future_date).exists())

    def test_booking_prevents_double_booking(self):
        self.client.login(username="patient_jane", password="password123")
        future_date = timezone.localdate() + timedelta(days=2)

        # Existing active appointment
        Appointment.objects.create(
            patient=self.other_patient,
            doctor=self.doctor,
            date=future_date,
            time=time(14, 0),
            reason='First booking',
            status='Confirmed'
        )

        # Jane tries to book the same slot
        response = self.client.post(reverse('book_appointment', args=[self.doctor.id]), {
            'date': future_date.strftime('%Y-%m-%d'),
            'time': "14:00",
            'reason': 'Conflicting booking'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already booked")

    # --- Cancellation Tests ---
    def test_patient_can_cancel_own_appointment(self):
        self.client.login(username="patient_jane", password="password123")
        future_date = timezone.localdate() + timedelta(days=2)
        app = Appointment.objects.create(
            patient=self.patient_user,
            doctor=self.doctor,
            date=future_date,
            time=time(11, 0),
            reason='Need to cancel',
            status='Pending'
        )

        response = self.client.post(reverse('cancel_appointment', args=[app.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        app.refresh_from_db()
        self.assertEqual(app.status, 'Cancelled')

    def test_other_patient_cannot_cancel_appointment(self):
        self.client.login(username="patient_mark", password="password123")
        future_date = timezone.localdate() + timedelta(days=2)
        app = Appointment.objects.create(
            patient=self.patient_user,
            doctor=self.doctor,
            date=future_date,
            time=time(11, 0),
            reason='Jane appointment',
            status='Pending'
        )

        response = self.client.post(reverse('cancel_appointment', args=[app.id]), follow=True)
        app.refresh_from_db()
        self.assertNotEqual(app.status, 'Cancelled')

    def test_completed_appointment_cannot_be_cancelled(self):
        self.client.login(username="patient_jane", password="password123")
        app = Appointment.objects.create(
            patient=self.patient_user,
            doctor=self.doctor,
            date=timezone.localdate() - timedelta(days=1),
            time=time(11, 0),
            reason='Finished visit',
            status='Completed'
        )

        response = self.client.post(reverse('cancel_appointment', args=[app.id]), follow=True)
        app.refresh_from_db()
        self.assertEqual(app.status, 'Completed')

    # --- Doctor Management Tests ---
    def test_doctor_confirm_appointment(self):
        self.client.login(username="dr_smith", password="password123")
        future_date = timezone.localdate() + timedelta(days=1)
        app = Appointment.objects.create(
            patient=self.patient_user,
            doctor=self.doctor,
            date=future_date,
            time=time(10, 0),
            reason='Heart murmur inquiry',
            status='Pending'
        )

        response = self.client.post(reverse('update_appointment_status', args=[app.id, 'confirm']), follow=True)
        self.assertEqual(response.status_code, 200)
        app.refresh_from_db()
        self.assertEqual(app.status, 'Confirmed')

    def test_doctor_reject_appointment(self):
        self.client.login(username="dr_smith", password="password123")
        future_date = timezone.localdate() + timedelta(days=1)
        app = Appointment.objects.create(
            patient=self.patient_user,
            doctor=self.doctor,
            date=future_date,
            time=time(10, 0),
            reason='Doctor emergency leaves slot',
            status='Pending'
        )

        response = self.client.post(reverse('update_appointment_status', args=[app.id, 'reject']), follow=True)
        self.assertEqual(response.status_code, 200)
        app.refresh_from_db()
        self.assertEqual(app.status, 'Rejected')

    def test_doctor_complete_appointment_with_notes(self):
        self.client.login(username="dr_smith", password="password123")
        today = timezone.localdate()
        app = Appointment.objects.create(
            patient=self.patient_user,
            doctor=self.doctor,
            date=today,
            time=time(10, 0),
            reason='Consultation today',
            status='Confirmed'
        )

        clinical_notes = "BP 120/80. Prescribed Beta-blockers once daily. Follow up in 3 months."
        response = self.client.post(reverse('update_appointment_status', args=[app.id, 'complete']), {
            'doctor_notes': clinical_notes
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        app.refresh_from_db()
        self.assertEqual(app.status, 'Completed')
        self.assertEqual(app.doctor_notes, clinical_notes)

    def test_other_doctor_cannot_update_status(self):
        self.client.login(username="dr_jones", password="password123")
        app = Appointment.objects.create(
            patient=self.patient_user,
            doctor=self.doctor,
            date=timezone.localdate() + timedelta(days=1),
            time=time(10, 0),
            reason='Smith appointment',
            status='Pending'
        )

        response = self.client.post(reverse('update_appointment_status', args=[app.id, 'confirm']), follow=True)
        app.refresh_from_db()
        self.assertEqual(app.status, 'Pending')

    # --- Admin Portal Management Tests ---
    def test_admin_can_access_dashboard_and_modules(self):
        self.client.login(username="admin_boss", password="password123")
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hospital Management Dashboard")

        resp_depts = self.client.get(reverse('admin_department_list'))
        self.assertEqual(resp_depts.status_code, 200)

        resp_docs = self.client.get(reverse('admin_doctor_list'))
        self.assertEqual(resp_docs.status_code, 200)

        resp_pts = self.client.get(reverse('admin_patient_list'))
        self.assertEqual(resp_pts.status_code, 200)

        resp_apps = self.client.get(reverse('admin_appointment_list'))
        self.assertEqual(resp_apps.status_code, 200)

    def test_admin_can_create_and_delete_department(self):
        self.client.login(username="admin_boss", password="password123")
        response = self.client.post(reverse('admin_department_create'), {
            'name': 'Dermatology & Skin Care',
            'description': 'Comprehensive skin wellness and diagnosis.',
            'icon': 'fa-allergies'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Department.objects.filter(name='Dermatology & Skin Care').exists())

        dept = Department.objects.get(name='Dermatology & Skin Care')
        del_resp = self.client.post(reverse('admin_department_delete', args=[dept.id]), follow=True)
        self.assertEqual(del_resp.status_code, 200)
        self.assertFalse(Department.objects.filter(name='Dermatology & Skin Care').exists())

    def test_admin_can_enroll_doctor(self):
        self.client.login(username="admin_boss", password="password123")
        response = self.client.post(reverse('admin_doctor_create'), {
            'username': 'dr_new_specialist',
            'first_name': 'Gregory',
            'last_name': 'House',
            'email': 'house@diagnostics.hospital',
            'phone': '+1 555-888-0000',
            'password': 'doctorpass123',
            'department': self.dept_neuro.id,
            'specialization': 'Diagnostic Medicine',
            'experience': 20,
            'fee': '250.00',
            'working_hours_start': '08:00',
            'working_hours_end': '16:00',
            'room_number': 'Suite 404',
            'bio': 'Board-certified diagnostician specializing in complex neurological and infectious ailments.'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='dr_new_specialist', role='doctor').exists())
        self.assertTrue(Doctor.objects.filter(specialization='Diagnostic Medicine').exists())

    def test_admin_can_update_appointment_status(self):
        self.client.login(username="admin_boss", password="password123")
        app = Appointment.objects.create(
            patient=self.patient_user,
            doctor=self.doctor,
            date=timezone.localdate() + timedelta(days=2),
            time=time(11, 0),
            reason='Need admin status audit',
            status='Pending'
        )

        response = self.client.get(reverse('admin_appointment_update_status', args=[app.id, 'confirm']), follow=True)
        self.assertEqual(response.status_code, 200)
        app.refresh_from_db()
        self.assertEqual(app.status, 'Confirmed')

        # Admin can also cancel
        response = self.client.get(reverse('admin_appointment_update_status', args=[app.id, 'cancel']), follow=True)
        self.assertEqual(response.status_code, 200)
        app.refresh_from_db()
        self.assertEqual(app.status, 'Cancelled')

    def test_non_admin_cannot_access_admin_crud(self):
        self.client.login(username="patient_jane", password="password123")
        response = self.client.get(reverse('admin_department_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('patient_dashboard'))

        self.client.login(username="dr_smith", password="password123")
        response = self.client.get(reverse('admin_doctor_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('doctor_dashboard'))

