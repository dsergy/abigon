from django.shortcuts import render  
from ads.models import Ad  

def home(request):  
    vip_ads = Ad.objects.filter(status='published')[:3]  
    return render(request, 'home.html', {'vip_ads': vip_ads})