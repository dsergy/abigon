# classifieds/views.py  

from ads.models import Ad  
from django.shortcuts import render, redirect  
from django.contrib.auth.forms import UserCreationForm  
from django.contrib.auth import login

def home(request):  
    """Home page view."""
    latest_ads = Ad.objects.filter(status='published').order_by('-created_at')[:6]
    return render(request, 'home.html', {
        'latest_ads': latest_ads,
    })  

def register(request):  
    if request.method == 'POST':  
        form = UserCreationForm(request.POST)  
        if form.is_valid():  
            user = form.save()  
            login(request, user)  
            return redirect('home')  
    else:  
        form = UserCreationForm()  
    return render(request, 'registration/register.html', {'form': form})