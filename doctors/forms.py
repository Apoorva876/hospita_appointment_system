from django import forms
from django.core.exceptions import ValidationError
from accounts.models import User
from .models import Department, Doctor


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Cardiology'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Overview of department medical services...'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fa-stethoscope'}),
        }


class AdminDoctorCreateForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Username (e.g. dr_smith)'
    }))
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'First Name'
    }))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Last Name'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'doctor@medicare.hospital'
    }))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Contact phone'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Password (min. 6 characters)'
    }))

    class Meta:
        model = Doctor
        fields = [
            'department', 'specialization', 'experience', 'fee',
            'working_hours_start', 'working_hours_end', 'room_number', 'bio'
        ]
        widgets = {
            'department': forms.Select(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Interventional Cardiology'}),
            'experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'working_hours_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'working_hours_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Room / Cabin / Wing'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Professional medical biography...'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("A user with this username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this email address already exists.")
        return email

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            phone=self.cleaned_data.get('phone', ''),
            role='doctor',
            is_staff=False
        )
        doctor = super().save(commit=False)
        doctor.user = user
        if commit:
            doctor.save()
        return doctor


class AdminDoctorEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Doctor
        fields = [
            'department', 'specialization', 'experience', 'fee',
            'working_hours_start', 'working_hours_end', 'room_number', 'bio'
        ]
        widgets = {
            'department': forms.Select(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'working_hours_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'working_hours_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['phone'].initial = self.instance.user.phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        current_user = self.instance.user
        if User.objects.filter(email__iexact=email).exclude(pk=current_user.pk).exists():
            raise ValidationError("A user with this email address already exists.")
        return email

    def save(self, commit=True):
        doctor = super().save(commit=False)
        user = doctor.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.save()
        if commit:
            doctor.save()
        return doctor
