from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
import jwt
import random
from datetime import datetime, timedelta

User = get_user_model()

def login_view(request):
    """Handle login form display and submission."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                remember = request.POST.get('remember')
                if not remember:
                    request.session.set_expiry(0)
                return HttpResponse('<script>window.location.reload()</script>')
        return render(request, 'accounts/login_modal.html', {'form': form})
    
    form = AuthenticationForm()
    return render(request, 'accounts/login_modal.html', {'form': form})

def generate_verification_code():
    return str(random.randint(100000, 999999))

def generate_token(email, code):
    payload = {
        'email': email,
        'code': code,
        'exp': datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def verify_token(token):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except:
        return None

def register_modal(request):
    return render(request, 'accounts/register_modal.html')

def register_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if not email:
            return render(request, 'accounts/register_modal.html', {
                'error': 'Email is required'
            })
            
        if User.objects.filter(email=email).exists():
            return render(request, 'accounts/register_modal.html', {
                'error': 'This email is already registered'
            })
        
        code = generate_verification_code()
        token = generate_token(email, code)
        request.session['registration_token'] = token
        
        try:
            send_mail(
                'Verification Code',
                f'Your verification code is: {code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            return render(request, 'accounts/register_modal.html', {
                'error': f'Failed to send verification code: {str(e)}'
            })
        
        return render(request, 'accounts/verify_code.html', {'email': email})
    
    return HttpResponse('Invalid request', status=400)

def verify_code(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('code')
        token = request.session.get('registration_token')
        
        payload = verify_token(token)
        if not payload or payload['email'] != email or payload['code'] != code:
            return render(request, 'accounts/verify_code.html', {
                'error': 'Invalid code',
                'email': email
            })
        
        return render(request, 'accounts/set_password.html', {
            'email': email,
            'token': token
        })
    
    return HttpResponse('Invalid request', status=400)

def complete_registration(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        token = request.POST.get('token')
        
        if password1 != password2:
            return render(request, 'accounts/set_password.html', {
                'error': 'Passwords do not match',
                'email': email,
                'token': token
            })
            
        payload = verify_token(token)
        if not payload or payload['email'] != email:
            return render(request, 'accounts/set_password.html', {
                'error': 'Invalid token',
                'email': email,
                'token': token
            })
            
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password1
            )
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return HttpResponse('<script>window.location.href="/";</script>')
        except Exception as e:
            return render(request, 'accounts/set_password.html', {
                'error': str(e),
                'email': email,
                'token': token
            })
    
    return HttpResponse('Invalid request', status=400)

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {
        'user': request.user
    })

def logout_view(request):
    logout(request)
    return redirect('/')
