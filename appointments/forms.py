from django import forms
from django.core.exceptions import ValidationError
from .models import Appointment
from datetime import datetime, timedelta


class BookingForm(forms.ModelForm):
    provider = forms.ModelChoiceField(
        queryset=None,
        empty_label="Select a service provider",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )

    class Meta:
        model = Appointment
        fields = ['provider', 'date', 'time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth.models import User
        from glambookapp.models import UserProfile
        
        # Get all staff members (providers)
        staff_profiles = UserProfile.objects.filter(role='staff')
        staff_users = [profile.user for profile in staff_profiles]
        self.fields['provider'].queryset = User.objects.filter(id__in=[u.id for u in staff_users])

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        provider = cleaned_data.get('provider')

        if date and time:
            # Check if date is not in the past
            appointment_datetime = datetime.combine(date, time)
            if appointment_datetime < datetime.now():
                raise ValidationError("Cannot book appointments in the past.")

            # Check if provider is already booked at that time
            if provider and Appointment.objects.filter(
                provider=provider,
                date=date,
                time=time
            ).exclude(status='cancelled').exists():
                raise ValidationError(f"This provider is not available at {time} on {date}.")

        return cleaned_data
