from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_customer')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_provider')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('provider', 'date', 'time')
        ordering = ['-date', '-time']

    def __str__(self):
        return f"Appointment: {self.customer.first_name} with {self.provider.first_name} on {self.date}"

    def is_upcoming(self):
        appointment_datetime = datetime.combine(self.date, self.time)
        return appointment_datetime > datetime.now() and self.status != 'cancelled'

    def is_past(self):
        appointment_datetime = datetime.combine(self.date, self.time)
        return appointment_datetime <= datetime.now()
