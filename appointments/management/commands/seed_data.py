import os
from datetime import time, date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User, PatientProfile
from doctors.models import Department, Doctor
from appointments.models import Appointment


class Command(BaseCommand):
    help = 'Seeds database with initial departments, doctors, demo patient, and admin user'

    def handle(self, *args, **options):
        self.stdout.write("Seeding hospital appointment system data...")

        # 1. Create Admin
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@medicare.hospital',
                'first_name': 'Hospital',
                'last_name': 'Administrator',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'phone': '+1 (555) 019-9000',
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user: admin / admin123"))
        else:
            self.stdout.write("Admin user already exists.")

        # 2. Create Departments
        departments_data = [
            {
                'name': 'Cardiology',
                'description': 'Comprehensive cardiac care including diagnostics, heart disease prevention, and post-operative monitoring.'
            },
            {
                'name': 'Neurology',
                'description': 'Advanced evaluation and therapeutic treatment for brain, spinal cord, and nervous system conditions.'
            },
            {
                'name': 'Orthopedics',
                'description': 'Surgical and non-surgical care for joint replacements, spine disorders, and sports injuries.'
            },
            {
                'name': 'Pediatrics',
                'description': 'Dedicated healthcare for newborns, children, and adolescents with compassionate specialist support.'
            },
            {
                'name': 'Dermatology',
                'description': 'Expert clinical dermatology for skin disorders, allergy management, and modern dermatological procedures.'
            },
            {
                'name': 'General Medicine',
                'description': 'Comprehensive outpatient consultations, routine wellness screenings, and chronic illness monitoring.'
            },
        ]

        dept_objs = {}
        for dept in departments_data:
            obj, _ = Department.objects.get_or_create(
                name=dept['name'],
                defaults={'description': dept['description']}
            )
            dept_objs[dept['name']] = obj
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(dept_objs)} departments."))

        # 3. Create Doctors
        doctors_data = [
            {
                'username': 'dr_sarah',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'email': 'sarah.johnson@medicare.hospital',
                'phone': '+1 (555) 012-3401',
                'department': dept_objs['Cardiology'],
                'specialization': 'Interventional Cardiology',
                'experience': 12,
                'fee': 120.00,
                'start': time(9, 0),
                'end': time(17, 0),
                'room': 'Wing B, Room 204',
                'bio': 'Dr. Sarah Johnson is a fellowship-trained cardiologist specializing in ischemic heart disease, cardiac imaging, and preventative cardiovascular health.'
            },
            {
                'username': 'dr_robert',
                'first_name': 'Robert',
                'last_name': 'Chen',
                'email': 'robert.chen@medicare.hospital',
                'phone': '+1 (555) 012-3402',
                'department': dept_objs['Neurology'],
                'specialization': 'Clinical Neurophysiology',
                'experience': 15,
                'fee': 150.00,
                'start': time(8, 30),
                'end': time(16, 30),
                'room': 'Neurology Pavilion, Suite 105',
                'bio': 'Dr. Robert Chen brings 15 years of neurological expertise focusing on migraines, seizure disorders, neuromuscular conditions, and cognitive health.'
            },
            {
                'username': 'dr_elena',
                'first_name': 'Elena',
                'last_name': 'Rostova',
                'email': 'elena.rostova@medicare.hospital',
                'phone': '+1 (555) 012-3403',
                'department': dept_objs['Orthopedics'],
                'specialization': 'Orthopedic & Joint Surgery',
                'experience': 9,
                'fee': 110.00,
                'start': time(10, 0),
                'end': time(18, 0),
                'room': 'Surgical Center, Room 310',
                'bio': 'Dr. Elena Rostova specializes in minimally invasive joint arthroscopy, reconstructive knee/shoulder procedures, and athletic sports rehabilitation.'
            },
            {
                'username': 'dr_marcus',
                'first_name': 'Marcus',
                'last_name': 'Adebayo',
                'email': 'marcus.adebayo@medicare.hospital',
                'phone': '+1 (555) 012-3404',
                'department': dept_objs['Pediatrics'],
                'specialization': 'Pediatric Medicine',
                'experience': 10,
                'fee': 90.00,
                'start': time(9, 0),
                'end': time(16, 0),
                'room': 'Children Clinic, Suite 102',
                'bio': 'Dr. Marcus Adebayo is devoted to developmental wellness, adolescent care, pediatric infectious diseases, and routine early childhood vaccinations.'
            },
            {
                'username': 'dr_lisa',
                'first_name': 'Lisa',
                'last_name': 'Montgomery',
                'email': 'lisa.montgomery@medicare.hospital',
                'phone': '+1 (555) 012-3405',
                'department': dept_objs['Dermatology'],
                'specialization': 'Medical & Cosmetic Dermatology',
                'experience': 7,
                'fee': 100.00,
                'start': time(9, 30),
                'end': time(17, 30),
                'room': 'Dermatology Wing, Room 114',
                'bio': 'Dr. Lisa Montgomery provides expert diagnosis for eczema, psoriasis, skin cancer screenings, and specialized laser clinical treatments.'
            },
            {
                'username': 'dr_david',
                'first_name': 'David',
                'last_name': 'Miller',
                'email': 'david.miller@medicare.hospital',
                'phone': '+1 (555) 012-3406',
                'department': dept_objs['General Medicine'],
                'specialization': 'Primary Care & Internal Medicine',
                'experience': 14,
                'fee': 80.00,
                'start': time(8, 0),
                'end': time(16, 0),
                'room': 'General OPD, Room 101',
                'bio': 'Dr. David Miller focuses on holistic patient wellness, routine annual health checkups, hypertension management, and lifestyle medicine.'
            },
        ]

        created_doctors = []
        for d in doctors_data:
            doc_user, u_created = User.objects.get_or_create(
                username=d['username'],
                defaults={
                    'first_name': d['first_name'],
                    'last_name': d['last_name'],
                    'email': d['email'],
                    'phone': d['phone'],
                    'role': 'doctor',
                    'is_staff': False,
                }
            )
            if u_created:
                doc_user.set_password('doctor123')
                doc_user.save()

            doctor_rec, _ = Doctor.objects.get_or_create(
                user=doc_user,
                defaults={
                    'department': d['department'],
                    'specialization': d['specialization'],
                    'experience': d['experience'],
                    'fee': d['fee'],
                    'working_hours_start': d['start'],
                    'working_hours_end': d['end'],
                    'room_number': d['room'],
                    'bio': d['bio'],
                }
            )
            created_doctors.append(doctor_rec)

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(created_doctors)} doctor profiles (password: doctor123)."))

        # 4. Create Demo Patient
        patient_user, p_created = User.objects.get_or_create(
            username='patient_john',
            defaults={
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@example.com',
                'phone': '+1 (555) 789-0123',
                'role': 'patient',
            }
        )
        if p_created:
            patient_user.set_password('patient123')
            patient_user.save()

        patient_profile, _ = PatientProfile.objects.get_or_create(
            user=patient_user,
            defaults={
                'date_of_birth': date(1992, 5, 14),
                'gender': 'Male',
                'blood_group': 'O+',
                'address': '742 Evergreen Terrace, Springfield',
                'emergency_contact': '+1 (555) 999-8877 (Jane Doe, Spouse)',
            }
        )
        self.stdout.write(self.style.SUCCESS("Loaded demo patient: patient_john / patient123"))

        # 5. Create Sample Appointments for Demonstration
        today = timezone.localdate()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=5)
        past_date = today - timedelta(days=3)

        # Appointment 1: Confirmed tomorrow
        Appointment.objects.get_or_create(
            patient=patient_user,
            doctor=created_doctors[0],  # Dr. Sarah Johnson
            date=tomorrow,
            time=time(10, 0),
            defaults={
                'reason': 'Routine annual cardiology checkup and follow-up on resting heart rate.',
                'status': 'Confirmed',
            }
        )

        # Appointment 2: Pending next week
        Appointment.objects.get_or_create(
            patient=patient_user,
            doctor=created_doctors[1],  # Dr. Robert Chen
            date=next_week,
            time=time(11, 0),
            defaults={
                'reason': 'Recurrent tension headaches in the morning and mild light sensitivity.',
                'status': 'Pending',
            }
        )

        # Appointment 3: Completed in past
        Appointment.objects.get_or_create(
            patient=patient_user,
            doctor=created_doctors[5],  # Dr. David Miller
            date=past_date,
            time=time(9, 30),
            defaults={
                'reason': 'Mild seasonal allergy and chest congestion examination.',
                'status': 'Completed',
                'doctor_notes': 'Patient examined. Lungs clear. Advised antihistamines once daily for 5 days with plenty of hydration.',
            }
        )

        self.stdout.write(self.style.SUCCESS("Loaded sample appointments."))
        self.stdout.write(self.style.SUCCESS("Hospital data seeding completed successfully!"))
