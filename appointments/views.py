from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .forms import BookingForm
from .models import Appointment


@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.customer = request.user
            appointment.save()
            messages.success(request, 'Appointment booked successfully.')
            send_appointment_email(
                appointment.customer.email,
                'Appointment confirmed',
                f'Your appointment with {appointment.provider.username} is booked for {appointment.date} at {appointment.time}.'
            )
            return redirect('my_appointments')
    else:
        form = BookingForm()

    return render(request, 'appointments/book.html', {'form': form})


@login_required
def my_appointments(request):
    user = request.user
    user_role = getattr(user.profile, 'role', 'customer') if hasattr(user, 'profile') else 'customer'

    appointments = Appointment.objects.filter(Q(customer=user) | Q(provider=user))
    if user_role == 'staff':
        appointments = appointments.filter(provider=user)
        page_title = 'My Schedule'
    else:
        appointments = appointments.filter(customer=user)
        page_title = 'My Appointments'

    upcoming = [appointment for appointment in appointments if appointment.is_upcoming()]
    past = [appointment for appointment in appointments if appointment.is_past()]

    return render(request, 'appointments/my_appointments.html', {
        'upcoming_appointments': upcoming,
        'past_appointments': past,
        'page_title': page_title,
        'user_role': user_role,
    })


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.user not in [appointment.customer, appointment.provider]:
        messages.error(request, 'You are not allowed to cancel this appointment.')
        return redirect('my_appointments')

    appointment.status = 'cancelled'
    appointment.save()
    messages.success(request, 'Appointment cancelled.')
    return redirect('my_appointments')


@login_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if appointment.customer != request.user:
        messages.error(request, 'Only the customer can reschedule this appointment.')
        return redirect('my_appointments')

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=appointment)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.status = 'rescheduled'
            appointment.save()
            messages.success(request, 'Appointment rescheduled.')
            return redirect('my_appointments')
    else:
        form = BookingForm(instance=appointment)
        form.fields['provider'].disabled = True

    return render(request, 'appointments/reschedule.html', {'form': form, 'appointment': appointment})


def send_appointment_email(to_email, subject, message):
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
    try:
        send_mail(subject, message, from_email, [to_email], fail_silently=True)
    except Exception:
        pass
