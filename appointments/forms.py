from datetime import datetime

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Appointment


class BookingForm(forms.ModelForm):
    provider = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__role='staff'),
        empty_label='Select provider',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Appointment
        fields = ['provider', 'date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        provider = cleaned_data.get('provider')
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if date and date < datetime.now().date():
            raise ValidationError('Please choose a future date for the appointment.')

        if provider and date and time:
            conflicts = Appointment.objects.filter(
                provider=provider,
                date=date,
                time=time
            ).exclude(status='cancelled')

            if self.instance.pk:
                conflicts = conflicts.exclude(pk=self.instance.pk)

            if conflicts.exists():
                raise ValidationError('That provider already has an appointment at this time.')

        return cleaned_data
