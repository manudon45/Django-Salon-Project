from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ServiceType
from .forms import ServiceTypeForm


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        profile = getattr(request.user, 'profile', None)
        if not profile or profile.role != 'admin':
            messages.error(request, 'Access denied. Admin only.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return login_required(wrapper)


@admin_required
def service_list(request):
    services = ServiceType.objects.all()
    return render(request, 'services/list.html', {'services': services})


@admin_required
def service_create(request):
    if request.method == 'POST':
        form = ServiceTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service type created.')
            return redirect('service_list')
    else:
        form = ServiceTypeForm()
    return render(request, 'services/form.html', {'form': form, 'action': 'Add'})


@admin_required
def service_edit(request, pk):
    service = get_object_or_404(ServiceType, pk=pk)
    if request.method == 'POST':
        form = ServiceTypeForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service type updated.')
            return redirect('service_list')
    else:
        form = ServiceTypeForm(instance=service)
    return render(request, 'services/form.html', {'form': form, 'action': 'Edit', 'service': service})


@admin_required
def service_delete(request, pk):
    service = get_object_or_404(ServiceType, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service type deleted.')
        return redirect('service_list')
    return render(request, 'services/confirm_delete.html', {'service': service})
