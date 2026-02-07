from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods

def login_view(request):
    """Login page with light green theme."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('/dashboard/')
        else:
            context = {
                'error': 'Invalid username or password'
            }
            return render(request, 'login.html', context, status=401)
    
    return render(request, 'login.html')

def signup_view(request):
    """Signup page with light green theme."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        chat_id = request.POST.get('chat_id')

        # Validate inputs
        if password != password_confirm:
            context = {'error': 'Passwords do not match'}
            return render(request, 'signup.html', context, status=400)

        if User.objects.filter(username=username).exists():
            context = {'error': 'Username already exists'}
            return render(request, 'signup.html', context, status=400)

        if User.objects.filter(email=email).exists():
            context = {'error': 'Email already registered'}
            return render(request, 'signup.html', context, status=400)

        if len(password) < 8:
            context = {'error': 'Password must be at least 8 characters'}
            return render(request, 'signup.html', context, status=400)

        if not chat_id or not chat_id.isdigit():
            context = {'error': 'Invalid Telegram Chat ID'}
            return render(request, 'signup.html', context, status=400)

        # Create user and profile
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            from .models import UserProfile
            UserProfile.objects.create(user=user, chat_id=chat_id)
            return render(request, 'signup_success.html')
        except Exception as e:
            context = {'error': 'An error occurred. Please try again.'}
            return render(request, 'signup.html', context, status=400)

    return render(request, 'signup.html')

def logic_page(request):
    """Standard logic page with light green theme."""
    context = {
        'title': 'Logic Page',
        'content': 'Welcome to the Logic Page'
    }
    return render(request, 'logic_page.html', context)
