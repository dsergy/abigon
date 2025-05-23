from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.contrib.auth import get_user_model, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.validators import RegexValidator
from django.views.decorators.http import require_POST, require_http_methods
from django.core.files.storage import default_storage
import json
import re
from django.template.loader import render_to_string
from datetime import datetime, date

from .auth_views import (
    login_view, logout_view, register_email, verify_code,
    complete_registration, password_reset_request,
    password_reset_verify, password_reset_confirm
)

User = get_user_model()

def get_recaptcha_context():
    """Get reCAPTCHA context for templates."""
    return {
        'recaptcha_site_key': settings.RECAPTCHA_PUBLIC_KEY
    }

def verify_recaptcha(token):
    """Verify reCAPTCHA token"""
    url = 'https://www.google.com/recaptcha/api/siteverify'
    data = {
        'secret': settings.RECAPTCHA_PRIVATE_KEY,
        'response': token
    }
    r = requests.post(url, data=data)
    result = r.json()
    return result.get('success', False) and result.get('score', 0) >= settings.RECAPTCHA_SCORE_THRESHOLD

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

@login_required
@require_POST
def update_name(request):
    """Update user's name."""
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        user = request.user
        user.name = name
        user.save()
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
        user = request.user
        user.age = age
        user.save()
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
        user = request.user
        user.gender = gender
        user.save()
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
        user = request.user
        
        # Delete old avatar if exists
        if user.avatar:
            default_storage.delete(user.avatar.path)
        
        user.avatar = avatar
        user.save()
        return JsonResponse({
            'status': 'success',
            'avatar_url': user.avatar.url
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
        user = request.user
        
        # Validate phone format
        phone_regex = RegexValidator(
            regex=r'^\+1 \(\d{3}\) \d{3}-\d{4}$',
            message="Phone number must be entered in the format: '+1 (XXX) XXX-XXXX'"
        )
        phone_regex(phone)
        
        # Reset verification if phone number changes
        if user.phone != phone:
            user.phone_verified = False
            
        user.phone = phone
        user.save()
        
        # Generate and send verification code if phone changed
        if not user.phone_verified:
            from .utils import generate_verification_code, generate_token
            code = generate_verification_code()
            token = generate_token(user.email, code)
            request.session['phone_verification_token'] = token
            # Here you would typically send an SMS, but for demo we'll use email
            send_mail(
                'Phone Verification Code',
                f'Your phone verification code is: {code}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
        return JsonResponse({
            'status': 'success',
            'phone': phone,
            'verified': user.phone_verified,
            'verification_needed': not user.phone_verified
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
        user = request.user
        
        from .utils import verify_token
        payload = verify_token(token)
        if not payload or payload['code'] != code:
            raise ValueError("Invalid verification code")
            
        user.phone_verified = True
        user.save()
        
        return JsonResponse({
            'status': 'success',
            'verified': True
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_POST
def update_zipcode(request):
    """Update user's zipcode."""
    try:
        data = json.loads(request.body)
        zipcode = data.get('zipcode', '').strip()
        user = request.user
        
        # Validate zipcode format
        zipcode_regex = RegexValidator(
            regex=r'^\d{5}$',
            message="Zipcode must be 5 digits"
        )
        zipcode_regex(zipcode)
            
        user.zipcode = zipcode
        user.save()
        
        return JsonResponse({
            'status': 'success',
            'zipcode': zipcode
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def delete_account(request):
    """Handle account deletion."""
    if request.method == 'POST':
        try:
            password = request.POST.get('password')
            user = request.user

            if not password:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Password is required to delete your account.'
                }, status=400)
            
            # Verify password
            if not user.check_password(password):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid password. Please try again.'
                }, status=400)

            # Delete user's avatar if exists
            if user.avatar:
                default_storage.delete(user.avatar.path)
            
            # Delete the user
            user.delete()
            
            # Logout the user
            logout(request)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Your account has been deleted successfully.'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return render(request, 'accounts/delete_account.html')

@require_http_methods(['GET'])
def login_modal(request):
    """Display login modal."""
    return render(request, 'accounts/modals/login_modal.html', get_recaptcha_context())

@login_required
@require_POST
def update_password(request):
    """Update user's password."""
    try:
        data = json.loads(request.body)
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return JsonResponse({
                'status': 'error',
                'message': 'Both current and new passwords are required.'
            }, status=400)
        
        # Verify current password
        if not request.user.check_password(current_password):
            return JsonResponse({
                'status': 'error',
                'message': 'Current password is incorrect.'
            }, status=400)
        
        # Set new password
        request.user.set_password(new_password)
        request.user.save()
        
        # Update session to prevent logout
        update_session_auth_hash(request, request.user)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Password updated successfully.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
@require_POST
def update_dob(request):
    """Update user's date of birth."""
    try:
        data = json.loads(request.body)
        date_of_birth = data.get('date_of_birth')
        
        if not date_of_birth:
            return JsonResponse({
                'status': 'error',
                'message': 'Date of birth is required.'
            }, status=400)
        
        # Validate date format
        try:
            dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid date format.'
            }, status=400)
        
        # Calculate age
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        # Update user's date of birth
        request.user.date_of_birth = dob
        request.user.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Date of birth updated successfully.',
            'age': age
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
