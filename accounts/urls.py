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
    path('profile/', views.profile_view, name='profile'),
] 