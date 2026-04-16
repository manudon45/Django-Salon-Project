from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Appointment
from .forms import BookingForm
from glambookapp.models import UserProfile


@login_required
def book_appointment(request):
    """Allow customers to book new appointments."""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.customer = request.user
            appointment.status = 'pending'
            appointment.save()

            # Send confirmation email
            try:
                send_mail(
                    subject='Appointment Booking Confirmation',
                    message=f"Your appointment has been scheduled for {appointment.date} at {appointment.time} with {appointment.provider.first_name}.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=True
                )
            except:
                pass

            messages.success(request, 'Appointment booked successfully!')
            return redirect('my_appointments')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookingForm()

    return render(request, 'appointments/book.html', {'form': form})


@login_required
def my_appointments(request):
    """Display user's appointments (customer bookings or staff schedule)."""
    user_profile = UserProfile.objects.get(user=request.user)
    
    if user_profile.role == 'staff':
        # Staff sees their schedule
        upcoming = Appointment.objects.filter(provider=request.user, status__in=['pending', 'confirmed']).order_by('date', 'time')
        past = Appointment.objects.filter(provider=request.user, status__in=['completed', 'cancelled']).order_by('-date', '-time')
    else:
        # Customers see their bookings
        upcoming = Appointment.objects.filter(customer=request.user, status__in=['pending', 'confirmed']).order_by('date', 'time')
        past = Appointment.objects.filter(customer=request.user, status__in=['completed', 'cancelled']).order_by('-date', '-time')

    context = {
        'upcoming': upcoming,
        'past': past,
        'is_staff': user_profile.role == 'staff'
    }

    return render(request, 'appointments/my_appointments.html', context)


@login_required
def cancel_appointment(request, appointment_id):
    """Cancel an appointment."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user is authorized
    if appointment.customer != request.user and appointment.provider != request.user:
        messages.error(request, 'You do not have permission to cancel this appointment.')
        return redirect('my_appointments')

    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully.')
        return redirect('my_appointments')

    return render(request, 'appointments/cancel.html', {'appointment': appointment})


@login_required
def reschedule_appointment(request, appointment_id):
    """Reschedule an existing appointment."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user is authorized
    if appointment.customer != request.user:
        messages.error(request, 'You do not have permission to reschedule this appointment.')
        return redirect('my_appointments')

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=appointment)
        if form.is_valid():
            updated_appointment = form.save(commit=False)
            updated_appointment.status = 'rescheduled'
            updated_appointment.save()
            messages.success(request, 'Appointment rescheduled successfully.')
            return redirect('my_appointments')
    else:
        form = BookingForm(instance=appointment)

    return render(request, 'appointments/reschedule.html', {'form': form, 'appointment': appointment})
