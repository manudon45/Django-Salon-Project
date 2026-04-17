from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment
from .forms import BookingForm, AssignStaffForm
from glambookapp.models import UserProfile


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        profile = getattr(request.user, 'profile', None)
        if not profile or profile.role != 'admin':
            messages.error(request, 'Access denied. Admin only.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return login_required(wrapper)


@login_required
def book_appointment(request):
    profile = getattr(request.user, 'profile', None)
    if profile and profile.role != 'customer':
        messages.error(request, 'Only customers can book appointments.')
        return redirect('home')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.customer = request.user
            appointment.status = 'pending'
            appointment.save()
            messages.success(request, 'Appointment booked successfully!')
            return redirect('my_appointments')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookingForm()

    return render(request, 'appointments/book.html', {'form': form})


@login_required
def my_appointments(request):
    user_profile = getattr(request.user, 'profile', None)
    role = user_profile.role if user_profile else 'customer'

    if role == 'staff':
        upcoming = Appointment.objects.filter(
            provider=request.user, status__in=['pending', 'confirmed']
        ).order_by('date', 'time')
        past = Appointment.objects.filter(
            provider=request.user, status__in=['completed', 'cancelled', 'rescheduled']
        ).order_by('-date', '-time')
    else:
        upcoming = Appointment.objects.filter(
            customer=request.user, status__in=['pending', 'confirmed', 'rescheduled']
        ).order_by('date', 'time')
        past = Appointment.objects.filter(
            customer=request.user, status__in=['completed', 'cancelled']
        ).order_by('-date', '-time')

    return render(request, 'appointments/my_appointments.html', {
        'upcoming': upcoming,
        'past': past,
        'is_staff': role == 'staff',
    })


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.customer != request.user:
        messages.error(request, 'You do not have permission to cancel this appointment.')
        return redirect('my_appointments')

    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled.')
        return redirect('my_appointments')

    return render(request, 'appointments/cancel.html', {'appointment': appointment})


@login_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.customer != request.user:
        messages.error(request, 'You do not have permission to reschedule this appointment.')
        return redirect('my_appointments')

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=appointment)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.status = 'rescheduled'
            updated.save()
            messages.success(request, 'Appointment rescheduled.')
            return redirect('my_appointments')
    else:
        form = BookingForm(instance=appointment)

    return render(request, 'appointments/reschedule.html', {'form': form, 'appointment': appointment})


@admin_required
def all_bookings(request):
    appointments = Appointment.objects.select_related('customer', 'provider', 'service').order_by('-date', '-time')
    return render(request, 'appointments/all_bookings.html', {'appointments': appointments})


@admin_required
def assign_staff(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        form = AssignStaffForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff assigned and status updated.')
            return redirect('all_bookings')
    else:
        form = AssignStaffForm(instance=appointment)

    return render(request, 'appointments/assign_staff.html', {'form': form, 'appointment': appointment})
