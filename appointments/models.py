from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_customer')
    provider = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments_as_provider')
    service = models.ForeignKey('services.ServiceType', on_delete=models.SET_NULL, null=True, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time']

    def __str__(self):
        service_name = self.service.name if self.service else 'Unknown Service'
        return f"{self.customer.first_name} — {service_name} on {self.date}"

    def is_upcoming(self):
        return datetime.combine(self.date, self.time) > datetime.now() and self.status != 'cancelled'

    def is_past(self):
        return datetime.combine(self.date, self.time) <= datetime.now()
