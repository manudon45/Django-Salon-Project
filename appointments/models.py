from datetime import datetime

from django.contrib.auth.models import User
from django.db import models


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointments_as_customer'
    )
    provider = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointments_as_provider'
    )
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )

    class Meta:
        ordering = ['-date', '-time']
        unique_together = ('provider', 'date', 'time')

    def __str__(self):
        return f"{self.customer.username} with {self.provider.username} on {self.date} at {self.time}"

    def is_upcoming(self):
        appointment_datetime = datetime.combine(self.date, self.time)
        return appointment_datetime >= datetime.now()

    def is_past(self):
        return not self.is_upcoming()
