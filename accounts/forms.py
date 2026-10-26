from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import PatientProfile
from doctors.models import Doctor

User = get_user_model()


class PatientRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First Name'
    }))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last Name'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email Address'
    }))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone Number'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password (min. 6 characters)'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm Password'
    }))

    # Patient profile fields
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date'
    }))
    gender = forms.ChoiceField(
        choices=[('', 'Select Gender')] + list(PatientProfile.GENDER_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    blood_group = forms.ChoiceField(
        choices=[('', 'Select Blood Group')] + list(PatientProfile.BLOOD_GROUP_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Residential Address'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        if password and len(password) < 6:
            self.add_error('password', "Password must be at least 6 characters.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            PatientProfile.objects.create(
                user=user,
                date_of_birth=self.cleaned_data.get('date_of_birth'),
                gender=self.cleaned_data.get('gender', ''),
                blood_group=self.cleaned_data.get('blood_group', ''),
                address=self.cleaned_data.get('address', '')
            )
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("An account with this email address already exists.")
        return email


class PatientProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['date_of_birth', 'gender', 'blood_group', 'emergency_contact', 'address']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency contact phone'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Residential address'}),
        }


class DoctorProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['specialization', 'experience', 'fee', 'working_hours_start', 'working_hours_end', 'room_number', 'bio']
        widgets = {
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'experience': forms.NumberInput(attrs={'class': 'form-control'}),
            'fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'working_hours_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'working_hours_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
