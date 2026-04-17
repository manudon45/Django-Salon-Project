from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Appointment
from services.models import ServiceType
from glambookapp.models import UserProfile
from datetime import datetime


class BookingForm(forms.ModelForm):
    service = forms.ModelChoiceField(
        queryset=ServiceType.objects.filter(is_active=True),
        empty_label="Select a service",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )

    class Meta:
        model = Appointment
        fields = ['service', 'date', 'time']

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if date and time:
            if datetime.combine(date, time) < datetime.now():
                raise ValidationError("Cannot book appointments in the past.")

        return cleaned_data


class AssignStaffForm(forms.ModelForm):
    provider = forms.ModelChoiceField(
        queryset=User.objects.none(),
        empty_label="Select staff member",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=Appointment.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Appointment
        fields = ['provider', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        staff_ids = UserProfile.objects.filter(role='staff').values_list('user_id', flat=True)
        self.fields['provider'].queryset = User.objects.filter(id__in=staff_ids)
