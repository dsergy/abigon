from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.core.validators import RegexValidator
import jwt
import random
from datetime import datetime, timedelta
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
import json
import re
import string

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
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'redirect': '/'})
                return redirect('home')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(f"{field}: {error}" if field != '__all__' else error)
            return JsonResponse({'error': ' '.join(errors)}, status=400)
        return render(request, 'accounts/login.html', {'form': form})
    
    form = AuthenticationForm()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'accounts/login_modal.html', {'form': form})
    return render(request, 'accounts/login.html', {'form': form})

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
    """Display registration modal."""
    return render(request, 'accounts/modals/register_modal.html')

@require_POST
def register_email(request):
    """Handle email registration."""
    try:
        print("Starting register_email view")
        email = request.POST.get('email')
        name = request.POST.get('name')
        print(f"Received data - email: {email}, name: {name}")

        if not all([email, name]):
            print("Missing required fields")
            return JsonResponse({
                'status': 'error',
                'message': 'All fields are required'
            }, status=400)

        if User.objects.filter(email=email).exists():
            print("Email already exists")
            return JsonResponse({
                'status': 'error',
                'message': 'This email is already registered'
            }, status=400)

        # Generate verification code
        verification_code = generate_verification_code()
        print(f"Generated verification code: {verification_code}")
        
        # Generate token
        token = generate_token(email, verification_code)
        print(f"Generated token: {token}")
        
        # Store in session
        request.session['registration_token'] = token
        request.session['registration_name'] = name
        print("Token and name stored in session")
        
        # Debug output
        print(f"Email settings:")
        print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        
        # Send verification email
        try:
            print("Attempting to send email...")
            send_mail(
                'Email Verification',
                f'Your verification code: {verification_code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            print("Email sent successfully")
        except Exception as e:
            print(f"Email error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to send verification email. Please try again.'
            }, status=500)
        
        context = {
            'email': email
        }
        print("Rendering verify_code template")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, 'accounts/modals/verify_code.html', context)
        return render(request, 'accounts/modals/verify_code.html', context)
    except Exception as e:
        print(f"General error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred. Please try again.'
        }, status=500)

def verify_code(request):
    """Handle verification code step."""
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('code')
        token = request.session.get('registration_token')
        
        payload = verify_token(token)
        if not payload or payload['email'] != email or payload['code'] != code:
            context = {
                'error': 'Invalid code',
                'email': email
            }
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render(request, 'accounts/verify_code.html', context)
            return render(request, 'accounts/verify_code.html', context)
        
        context = {
            'email': email,
            'token': token
        }
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, 'accounts/set_password.html', context)
        return render(request, 'accounts/set_password.html', context)
    
    return HttpResponse('Invalid request', status=400)

def complete_registration(request):
    """Complete registration process."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        token = request.POST.get('token')
        name = request.session.get('registration_name')
        
        if password1 != password2:
            context = {
                'error': 'Passwords do not match',
                'email': email,
                'token': token
            }
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render(request, 'accounts/set_password.html', context)
            return render(request, 'accounts/set_password.html', context)
            
        payload = verify_token(token)
        if not payload or payload['email'] != email:
            context = {
                'error': 'Invalid token',
                'email': email,
                'token': token
            }
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render(request, 'accounts/set_password.html', context)
            return render(request, 'accounts/set_password.html', context)
            
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password1,
                name=name
            )
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'redirect': '/'})
            return redirect('home')
        except Exception as e:
            context = {
                'error': str(e),
                'email': email,
                'token': token
            }
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render(request, 'accounts/set_password.html', context)
            return render(request, 'accounts/set_password.html', context)
    
    return HttpResponse('Invalid request', status=400)

@login_required
def profile_view(request):
    """Main profile view."""
    return render(request, 'accounts/profile.html', {
        'active_tab': 'profile'
    })

@login_required
def settings_view(request):
    """Settings view."""
    return render(request, 'accounts/settings.html', {
        'active_section': 'settings',
        'subsection': request.GET.get('subsection', 'account')
    })

@login_required
def profile_section(request, section):
    """Handle different profile sections."""
    if section == 'settings':
        return settings_view(request)
    
    template_name = f'accounts/{section}.html'
    return render(request, template_name, {
        'active_tab': section
    })

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
@require_POST
def update_name(request):
    """Update user's name."""
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        request.user.name = name
        request.user.save()
        return JsonResponse({'status': 'success', 'name': name})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_POST
def update_age(request):
    """Update user's age."""
    try:
        data = json.loads(request.body)
        age = data.get('age')
        if age is not None:
            age = int(age)
            if age < 13 or age > 120:
                raise ValueError("Age must be between 13 and 120")
        request.user.age = age
        request.user.save()
        return JsonResponse({'status': 'success', 'age': age})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_POST
def update_gender(request):
    """Update user's gender."""
    try:
        data = json.loads(request.body)
        gender = data.get('gender', '')
        if gender not in [choice[0] for choice in request.user.GENDER_CHOICES]:
            raise ValueError("Invalid gender choice")
        request.user.gender = gender
        request.user.save()
        return JsonResponse({'status': 'success', 'gender': gender})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_POST
def update_avatar(request):
    """Update user's avatar."""
    try:
        if 'avatar' not in request.FILES:
            raise ValueError("No avatar file provided")
        
        avatar = request.FILES['avatar']
        # Delete old avatar if exists
        if request.user.avatar:
            default_storage.delete(request.user.avatar.path)
        
        request.user.avatar = avatar
        request.user.save()
        return JsonResponse({
            'status': 'success',
            'avatar_url': request.user.avatar.url
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_POST
def update_phone(request):
    """Update user's phone number."""
    try:
        data = json.loads(request.body)
        phone = data.get('phone', '').strip()
        
        # Validate phone format
        phone_regex = RegexValidator(
            regex=r'^\+1 \(\d{3}\) \d{3}-\d{4}$',
            message="Phone number must be entered in the format: '+1 (XXX) XXX-XXXX'"
        )
        phone_regex(phone)
        
        # Reset verification if phone number changes
        if request.user.phone != phone:
            request.user.phone_verified = False
            
        request.user.phone = phone
        request.user.save()
        
        # Generate and send verification code if phone changed
        if not request.user.phone_verified:
            code = generate_verification_code()
            token = generate_token(request.user.email, code)
            request.session['phone_verification_token'] = token
            # Here you would typically send an SMS, but for demo we'll use email
            send_mail(
                'Phone Verification Code',
                f'Your phone verification code is: {code}',
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False,
            )
            
        return JsonResponse({
            'status': 'success',
            'phone': phone,
            'verified': request.user.phone_verified,
            'verification_needed': not request.user.phone_verified
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_POST
def verify_phone(request):
    """Verify phone number with code."""
    try:
        data = json.loads(request.body)
        code = data.get('code')
        token = request.session.get('phone_verification_token')
        
        payload = verify_token(token)
        if not payload or payload['code'] != code:
            raise ValueError("Invalid verification code")
            
        request.user.phone_verified = True
        request.user.save()
        
        return JsonResponse({
            'status': 'success',
            'verified': True
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_POST
def update_zipcode(request):
    """Update user's ZIP code."""
    try:
        data = json.loads(request.body)
        zip_code = data.get('zip_code', '').strip()
        
        # Validate ZIP code format
        if not re.match(r'^\d{5}(?:-\d{4})?$', zip_code):
            raise ValueError("ZIP code must be in format '12345' or '12345-6789'")
            
        request.user.zip_code = zip_code
        request.user.save()
        
        return JsonResponse({
            'status': 'success',
            'zip_code': zip_code
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@require_POST
@login_required
def delete_account(request):
    """Handle account deletion."""
    try:
        data = json.loads(request.body)
        email = data.get('email')

        if email != request.user.email:
            return JsonResponse({
                'status': 'error',
                'message': 'Email does not match your account email'
            }, status=400)

        # Send confirmation email
        send_mail(
            'Account Deletion Confirmation',
            f'Your account with email {email} has been successfully deleted.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        # Delete user
        user = request.user
        user.delete()

        # Logout user
        logout(request)

        return JsonResponse({
            'status': 'success',
            'message': 'Account successfully deleted'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
