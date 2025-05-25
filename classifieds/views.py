# classifieds/views.py  

from ads.models import Ad, PostStatus  
from django.shortcuts import render, redirect  
from django.contrib.auth.forms import UserCreationForm  
from django.contrib.auth import login

def home(request):  
    """Home page view."""
    published_status = PostStatus.objects.get(name='published')
    latest_ads = Ad.objects.filter(status=published_status).order_by('-created_at')[:6]
    return render(request, 'pages/home.html', {
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
    return render(request, 'accounts/auth/register.html', {'form': form})

def services(request):
    """View for services page."""
    return render(request, 'pages/services.html')

def events(request):
    """View for events page."""
    return render(request, 'pages/events.html')

def handler404(request, exception):
    """Handle 404 errors."""
    return render(request, '404.html', status=404)

def handler500(request):
    """Handle 500 errors."""
    return render(request, '500.html', status=500)