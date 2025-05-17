from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/modal/', views.register_modal, name='register_modal'),
    path('register/email/', views.register_email, name='register_email'),
    path('register/verify/', views.verify_code, name='verify_code'),
    path('register/complete/', views.complete_registration, name='complete_registration'),
    
    # Profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/settings/', views.settings_view, name='settings'),
    path('profile/<str:section>/', views.profile_section, name='profile_section'),
    
    # Profile Settings Update URLs
    path('profile/settings/update/name/', views.update_name, name='update_name'),
    path('profile/settings/update/age/', views.update_age, name='update_age'),
    path('profile/settings/update/gender/', views.update_gender, name='update_gender'),
    path('profile/settings/update/avatar/', views.update_avatar, name='update_avatar'),
    path('profile/settings/update/phone/', views.update_phone, name='update_phone'),
    path('profile/settings/update/phone/verify/', views.verify_phone, name='verify_phone'),
    path('profile/settings/update/zipcode/', views.update_zipcode, name='update_zipcode'),
] 