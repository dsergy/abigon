from django.urls import path
from . import views
from .auth_views import (
    login_view, logout_view, register_email, verify_code,
    complete_registration, password_reset_request,
    password_reset_verify, password_reset_confirm,
    register_modal
)

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', login_view, name='login'),
    path('login/modal/', views.login_modal, name='login_modal'),
    path('logout/', logout_view, name='logout'),
    
    # Registration URLs
    path('register/', register_modal, name='register'),
    path('register/email/', register_email, name='register_email'),
    path('verify/code/', verify_code, name='verify_code'),
    path('complete-registration/', complete_registration, name='complete_registration'),
    
    # Password Reset URLs
    path('password-reset/', password_reset_request, name='password_reset'),
    path('password-reset/verify/', password_reset_verify, name='password_reset_verify'),
    path('password-reset/confirm/', password_reset_confirm, name='password_reset_confirm'),
    
    # Profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('profile/<str:section>/', views.profile_section, name='profile_section'),
    
    # Profile Settings Update URLs
    path('profile/settings/update/name/', views.update_name, name='update_name'),
    path('profile/settings/update/age/', views.update_age, name='update_age'),
    path('profile/settings/update/gender/', views.update_gender, name='update_gender'),
    path('profile/settings/update/avatar/', views.update_avatar, name='update_avatar'),
    path('profile/settings/update/phone/', views.update_phone, name='update_phone'),
    path('profile/settings/verify/phone/', views.verify_phone, name='verify_phone'),
    path('profile/settings/update/zipcode/', views.update_zipcode, name='update_zipcode'),
    path('profile/settings/update/password/', views.update_password, name='update_password'),
    path('profile/settings/update/dob/', views.update_dob, name='update_dob'),
    path('profile/settings/delete-account/', views.delete_account, name='delete_account'),
] 