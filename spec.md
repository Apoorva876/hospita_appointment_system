# Hospital Appointment System: Specification

Built with Django (Python), Django Templates and SQLite.

---

## 1. Overview

A web application where patients book appointments with doctors online, doctors manage their appointment requests, and admins manage the hospital data. It replaces manual and phone-based booking.

---

## 2. Users

| User | What they can do |
|------|------------------|
| **Patient** | Register, log in, browse doctors, book, view and cancel appointments |
| **Doctor** | Log in, view appointments, confirm, reject or complete them |
| **Admin** | Manage departments, doctors, patients and all appointments |

---

## 3. Features Required

### 3.1 Accounts
- Patient registration and login/logout
- Role-based access (patient, doctor, admin see different pages)
- Profile view and edit

### 3.2 Departments and Doctors
- Admin adds departments (Cardiology, Neurology, etc.)
- Admin adds doctors with department, specialization, experience, fee and working hours
- Patients browse the doctor list, filter by department and search by name
- Doctor detail page with a "Book Appointment" button

### 3.3 Appointment Booking
- Patient picks a doctor, date, time and gives a reason
- Past dates and times outside the doctor's working hours are rejected
- A slot already booked for that doctor is rejected (no double booking)
- Patient can cancel a pending or confirmed appointment

### 3.4 Appointment Management (Doctor)
- Doctor sees today's appointments and pending requests
- Doctor can confirm, reject or mark an appointment completed
- Doctor can add notes to an appointment

### 3.5 Dashboards
- Patient dashboard: upcoming and past appointments
- Doctor dashboard: today's list and pending requests
- Admin panel: search, filter and edit all records

---

## 4. How It Works

### 4.1 Booking Flow
1. Patient registers and logs in.
2. Patient browses doctors and opens one doctor's page.
3. Patient clicks **Book Appointment** and fills date, time and reason.
4. System checks the date, working hours and slot availability.
5. If valid, the appointment is saved with status **Pending**.
6. Doctor sees the request on their dashboard and confirms or rejects it.
7. Patient sees the updated status on their dashboard.
8. After the visit, the doctor marks it **Completed**.

### 4.2 Appointment Status Lifecycle

```
Pending -> Confirmed -> Completed
   |           |
   |           +-> Cancelled (by patient)
   +-> Rejected (by doctor)
   +-> Cancelled (by patient)
```

### 4.3 Rules
- A doctor cannot have two active appointments at the same date and time.
- Cancelled and rejected appointments free the slot.
- Only the owning patient can cancel; only the assigned doctor can confirm, reject or complete.
- Completed appointments cannot be cancelled.
- Patients cannot open doctor or admin pages.

---

## 5. Application Structure

### 5.1 Architecture (Django MVT)

```
Browser -> urls.py -> views.py -> models.py -> Database
                         |
                         +-> templates (HTML) -> Browser
```

- **Model:** database tables
- **View:** logic that handles requests
- **Template:** HTML pages shown to the user

### 5.2 Folder Structure

```
hospital_project/
├── manage.py
├── hospital_project/        # settings and main urls
├── accounts/                # users, login, registration, profile
├── doctors/                 # departments and doctors
├── appointments/            # booking and status management
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── accounts/            # login, register, profile
│   ├── doctors/             # doctor list, doctor detail
│   └── appointments/        # book, patient dashboard, doctor dashboard
└── static/                  # css, js, images
```

### 5.3 Apps and Their Role

| App | Responsibility |
|-----|----------------|
| accounts | User model with role, registration, login, profile |
| doctors | Departments and doctor details, doctor list and detail pages |
| appointments | Booking, cancelling, status updates, dashboards |

### 5.4 Database Tables

| Table | Main Fields |
|-------|-------------|
| **User** | username, email, password, role, phone |
| **PatientProfile** | user, date of birth, gender, address, blood group |
| **Department** | name, description |
| **Doctor** | user, department, specialization, experience, fee, working hours |
| **Appointment** | patient, doctor, date, time, reason, status, doctor notes |

**Relationships**
- One Department has many Doctors
- One Doctor has many Appointments
- One Patient (User) has many Appointments
- One User has one PatientProfile or one Doctor record

### 5.5 Pages (URLs)

| Page | URL | Who |
|------|-----|-----|
| Home | `/` | Everyone |
| Register | `/accounts/register/` | Everyone |
| Login / Logout | `/accounts/login/`, `/accounts/logout/` | Everyone |
| Profile | `/accounts/profile/` | Logged in |
| Doctor list | `/doctors/` | Everyone |
| Doctor detail | `/doctors/<id>/` | Everyone |
| Book appointment | `/appointments/book/<doctor_id>/` | Patient |
| Patient dashboard | `/appointments/my/` | Patient |
| Cancel appointment | `/appointments/<id>/cancel/` | Patient |
| Doctor dashboard | `/appointments/doctor/` | Doctor |
| Update status | `/appointments/<id>/status/<action>/` | Doctor |
| Admin panel | `/admin/` | Admin |

### 5.6 Templates

| Template | Purpose |
|----------|---------|
| base.html | Common layout: navbar, messages, footer |
| home.html | Landing page with departments and a booking button |
| login / register / profile | Account pages |
| doctor_list.html | Doctor cards with filter and search |
| doctor_detail.html | Doctor information and Book Now button |
| book.html | Appointment booking form |
| patient_dashboard.html | Patient's appointments with cancel option |
| doctor_dashboard.html | Doctor's appointments with confirm, reject, complete options |
