from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.views.decorators.http import require_POST, require_http_methods
from django.template.loader import render_to_string
import jwt
import random
import string
from datetime import datetime, timedelta
import secrets
from django.core.cache import cache

from .utils import (
    get_recaptcha_context, verify_recaptcha, generate_verification_code,
    generate_token, verify_token, send_verification_email
)

User = get_user_model()

def login_view(request):
    """Handle login form display and submission."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        website = request.POST.get('website', '')  # Get honeypot field
        recaptcha_token = request.POST.get('g-recaptcha-response')
        
        # Check honeypot
        if website:  # If honeypot field is filled, it's a bot
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid form submission'
                }, status=400)
            return render(request, 'accounts/modals/login_modal.html', {
                'error': 'Invalid form submission',
                **get_recaptcha_context()
            })
        
        # Verify reCAPTCHA
        if not recaptcha_token or not verify_recaptcha(recaptcha_token):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid reCAPTCHA. Please try again.'
                }, status=400)
            return render(request, 'accounts/modals/login_modal.html', {
                'error': 'Invalid reCAPTCHA. Please try again.',
                **get_recaptcha_context()
            })
        
        if not email or not password:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Email and password are required'
                }, status=400)
            return render(request, 'accounts/modals/login_modal.html', {
                'error': 'Email and password are required',
                **get_recaptcha_context()
            })
        
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'redirect': '/'
                })
            return redirect('home')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid email or password'
            }, status=400)
        return render(request, 'accounts/modals/login_modal.html', {
            'error': 'Invalid email or password',
            **get_recaptcha_context()
        })
    
    # For GET requests, always return the modal template
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'accounts/modals/login_modal.html', get_recaptcha_context())
    return render(request, 'accounts/modals/login_modal.html', get_recaptcha_context())

def logout_view(request):
    logout(request)
    return redirect('home')

def register_modal(request):
    """Display registration modal."""
    return render(request, 'accounts/modals/register_modal.html', get_recaptcha_context())

@require_POST
def register_email(request):
    """Handle email registration."""
    try:
        email = request.POST.get('email')
        name = request.POST.get('name')
        website = request.POST.get('website', '')  # Get honeypot field
        recaptcha_token = request.POST.get('g-recaptcha-response')
        
        # Check honeypot
        if website:  # If honeypot field is filled, it's a bot
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid form submission'
                }, status=400)
            return render(request, 'accounts/modals/register_modal.html', {
                'error': 'Invalid form submission',
                **get_recaptcha_context()
            })

        # Verify reCAPTCHA
        if not recaptcha_token or not verify_recaptcha(recaptcha_token):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid reCAPTCHA. Please try again.'
                }, status=400)
            return render(request, 'accounts/modals/register_modal.html', {
                'error': 'Invalid reCAPTCHA. Please try again.',
                **get_recaptcha_context()
            })

        if not all([email, name]):
            return JsonResponse({
                'status': 'error',
                'message': 'All fields are required'
            }, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'This email is already registered'
            }, status=400)

        # Generate verification code
        verification_code = generate_verification_code()
        
        # Generate token
        token = generate_token(email, verification_code)
        
        # Store in session
        request.session['registration_token'] = token
        request.session['registration_name'] = name
        
        # Send verification email
        try:
            send_verification_email(email, verification_code)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to send verification email. Please try again.'
            }, status=500)
        
        context = {
            'email': email
        }
        
        # Always return JSON for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string('accounts/modals/verify_code.html', context, request)
            return JsonResponse({
                'status': 'success',
                'html': html
            })
        return render(request, 'accounts/modals/verify_code.html', context)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@require_http_methods(["GET", "POST"])
def verify_code(request):
    """Handle verification code step."""
    if request.method == "GET":
        # Get email from session
        email = request.session.get('registration_email')
        if not email:
            return JsonResponse({
                'status': 'error',
                'message': 'Email not found. Please start the registration process again.'
            }, status=400)
            
        return render(request, 'accounts/modals/verify_code.html', {'email': email})
        
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('code')
        website = request.POST.get('website', '')  # Get honeypot field
        
        # Check honeypot
        if website:  # If honeypot field is filled, it's a bot
            context = {
                'error': 'Invalid form submission',
                'email': email
            }
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('accounts/modals/verify_code.html', context, request)
                return JsonResponse({
                    'status': 'error',
                    'html': html
                })
            return render(request, 'accounts/modals/verify_code.html', context)
            
        token = request.session.get('registration_token')
        payload = verify_token(token)
        if not payload or payload['email'] != email or payload['code'] != code:
            context = {
                'error': 'Invalid code',
                'email': email
            }
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('accounts/modals/verify_code.html', context, request)
                return JsonResponse({
                    'status': 'error',
                    'html': html
                })
            return render(request, 'accounts/modals/verify_code.html', context)
        
        context = {
            'email': email,
            'token': token
        }
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string('accounts/modals/set_password.html', context, request)
            return JsonResponse({
                'status': 'success',
                'html': html
            })
        return render(request, 'accounts/modals/set_password.html', context)
    
    return HttpResponse('Invalid request', status=400)

def complete_registration(request):
    """Complete registration process."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        token = request.POST.get('token')
        website = request.POST.get('website', '')  # Get honeypot field
        
        # Check honeypot
        if website:  # If honeypot field is filled, it's a bot
            context = {
                'error': 'Invalid form submission',
                'email': email,
                'token': token
            }
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('accounts/modals/set_password.html', context, request)
                return JsonResponse({
                    'status': 'error',
                    'html': html
                })
            return render(request, 'accounts/modals/set_password.html', context)
            
        name = request.session.get('registration_name')
        
        if password1 != password2:
            context = {
                'error': 'Passwords do not match',
                'email': email,
                'token': token
            }
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('accounts/modals/set_password.html', context, request)
                return JsonResponse({
                    'status': 'error',
                    'html': html
                })
            return render(request, 'accounts/modals/set_password.html', context)
            
        payload = verify_token(token)
        if not payload or payload['email'] != email:
            context = {
                'error': 'Invalid token',
                'email': email,
                'token': token
            }
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('accounts/modals/set_password.html', context, request)
                return JsonResponse({
                    'status': 'error',
                    'html': html
                })
            return render(request, 'accounts/modals/set_password.html', context)
            
        try:
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'A user with this email already exists. Please try logging in instead.'
                }, status=400)

            # Generate a unique username if email is already taken as username
            username = email
            if User.objects.filter(username=username).exists():
                username = f"{email}_{secrets.token_hex(4)}"

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                name=name
            )
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'redirect': '/'
                })
            return redirect('home')
        except Exception as e:
            context = {
                'error': str(e),
                'email': email,
                'token': token
            }
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('accounts/modals/set_password.html', context, request)
                return JsonResponse({
                    'status': 'error',
                    'html': html
                })
            return render(request, 'accounts/modals/set_password.html', context)
    
    return HttpResponse('Invalid request', status=400)

def password_reset_request(request):
    """Handle password reset request."""
    if request.method == 'POST':
        email = request.POST.get('email')
        website = request.POST.get('website', '')  # Honeypot field
        recaptcha_token = request.POST.get('g-recaptcha-response')
        
        # Check honeypot
        if website:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid form submission'
            }, status=400)
        
        # Verify reCAPTCHA
        if not recaptcha_token or not verify_recaptcha(recaptcha_token):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid reCAPTCHA. Please try again.'
            }, status=400)
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'No user found with this email address.'
            }, status=400)
        
        # Generate and store verification code
        code = generate_verification_code()
        cache_key = f'password_reset_code_{email}'
        cache.set(cache_key, code, timeout=300)  # Code expires in 5 minutes
        
        # Store email in session
        request.session['reset_email'] = email
        
        # Send verification email
        try:
            send_verification_email(email, code)
            return JsonResponse({
                'status': 'success',
                'message': 'Verification code sent to your email.'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to send verification email. Please try again.'
            }, status=500)
    
    # For GET requests, return the modal template
    try:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string('accounts/modals/email_modal_pr.html', {}, request)
            return JsonResponse({
                'status': 'success',
                'html': html
            })
        return render(request, 'accounts/modals/email_modal_pr.html')
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': str(e) or 'Failed to load password reset form.'
            }, status=500)
        raise

@require_http_methods(["GET", "POST"])
def password_reset_verify(request):
    if request.method == "GET":
        # Get email from session
        email = request.session.get('reset_email')
        if not email:
            return JsonResponse({
                'status': 'error',
                'message': 'Email not found. Please start the password reset process again.'
            }, status=400)
            
        return render(request, 'accounts/modals/verify_modal_pr.html', {'email': email})
        
    code = request.POST.get('code')
    email = request.POST.get('email')

    if not code or not email:
        return JsonResponse({
            'status': 'error',
            'message': 'Missing required fields'
        }, status=400)

    # Get the stored code from cache
    cache_key = f'password_reset_code_{email}'
    stored_code = cache.get(cache_key)

    if not stored_code or stored_code != code:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid or expired verification code'
        }, status=400)

    # Generate a reset token
    reset_token = secrets.token_urlsafe(32)
    # Store the token in cache with a timeout of 5 minutes
    token_cache_key = f'password_reset_token_{email}'
    cache.set(token_cache_key, reset_token, timeout=300)

    # Store email and token in session
    request.session['reset_email'] = email
    request.session['reset_token'] = reset_token

    return JsonResponse({
        'status': 'success',
        'message': 'Code verified successfully',
        'email': email,
        'token': reset_token
    })

def password_reset_confirm(request):
    """Set new password."""
    if request.method == 'POST':
        email = request.POST.get('email')
        token = request.POST.get('token')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        website = request.POST.get('website', '')  # Honeypot field
        
        # Check honeypot
        if website:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid form submission'
            }, status=400)
        
        # Verify token from both cache and session
        token_cache_key = f'password_reset_token_{email}'
        stored_token = cache.get(token_cache_key)
        session_token = request.session.get('reset_token')
        
        if not stored_token and not session_token:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid or expired reset token. Please start the password reset process again.'
            }, status=400)
            
        if token != stored_token and token != session_token:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid or expired reset token. Please start the password reset process again.'
            }, status=400)
        
        # Validate passwords
        if password1 != password2:
            return JsonResponse({
                'status': 'error',
                'message': 'Passwords do not match.'
            }, status=400)
        
        if len(password1) < 8:
            return JsonResponse({
                'status': 'error',
                'message': 'Password must be at least 8 characters long.'
            }, status=400)
        
        # Update password
        try:
            user = User.objects.get(email=email)
            
            # Check if the new password is the same as the current one
            if user.check_password(password1):
                # Return success but with a different message
                return JsonResponse({
                    'status': 'success',
                    'message': 'Your password has been reset successfully. You can now login with your password.',
                    'redirect': '/?message=Password+reset+successful.+Please+login+with+your+new+password.'
                })
            
            # Set new password
            user.set_password(password1)
            user.save()
            
            # Clear cache and session
            cache.delete(token_cache_key)
            cache.delete(f'password_reset_code_{email}')
            request.session.pop('reset_token', None)
            request.session.pop('reset_email', None)
            
            # Send confirmation email
            try:
                subject = 'Password Reset Successful'
                message = f'Your password has been successfully reset. If you did not make this change, please contact support immediately.'
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [email]
                send_mail(subject, message, from_email, recipient_list)
            except Exception as e:
                # Log the error but don't fail the request
                print(f"Failed to send password reset confirmation email: {e}")
            
            return JsonResponse({
                'status': 'success',
                'message': 'Your password has been reset successfully. You can now login with your new password.',
                'redirect': '/?message=Password+reset+successful.+Please+login+with+your+new+password.'
            })
        except User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'User not found. Please start the password reset process again.'
            }, status=400)
    
    # For GET requests, get email and token from session
    email = request.session.get('reset_email')
    if not email:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'Email not found. Please start the password reset process again.'
            }, status=400)
        return render(request, 'accounts/modals/set_password_pr.html', {
            'error': 'Email not found. Please start the password reset process again.'
        })
    
    # Get token from both cache and session
    token_cache_key = f'password_reset_token_{email}'
    token = cache.get(token_cache_key) or request.session.get('reset_token')
    
    if not token:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'Reset token not found or expired. Please start the password reset process again.'
            }, status=400)
        return render(request, 'accounts/modals/set_password_pr.html', {
            'error': 'Reset token not found or expired. Please start the password reset process again.'
        })
    
    # Return the template with email and token
    context = {
        'email': email,
        'token': token
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('accounts/modals/set_password_pr.html', context, request)
        return JsonResponse({
            'status': 'success',
            'html': html
        })
    return render(request, 'accounts/modals/set_password_pr.html', context) 