from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignupForm, LoginForm, ProfileForm
from .forms import SignupForm, LoginForm


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to GlamBook, {user.first_name}! Your account has been created.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignupForm()

    return render(request, 'glambookapp/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'home')
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'glambookapp/login.html', {'form': form})


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'glambookapp/profile.html', {'form': form})


@login_required
def tasks_view(request):
    profile = getattr(request.user, 'profile', None)
    role = profile.role if profile else 'customer'
    tasks = []

    if role == 'staff':
        tasks = [
            {'title': 'Check today\'s appointments', 'description': 'Review all scheduled client visits for today.'},
            {'title': 'Confirm service preparations', 'description': 'Prepare your workspace and tools for the next client.'},
        ]
    else:
        tasks = [
            {'title': 'Complete your profile', 'description': 'Make sure your email and name are correct.'},
            {'title': 'Book an appointment', 'description': 'Schedule a visit with a staff member at your convenience.'},
        ]

    return render(request, 'glambookapp/tasks.html', {'tasks': tasks, 'role': role})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def home_view(request):
    profile = getattr(request.user, 'profile', None)
    role = profile.role if profile else 'customer'
    return render(request, 'glambookapp/home.html', {'role': role})
