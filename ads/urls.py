from django.urls import path
from . import views

app_name = 'ads'

    
urlpatterns = [
    path('', views.AdListView.as_view(), name='ad_list'),
    path('create/', views.AdCreateView.as_view(), name='ad_create'),
    path('new-post/', views.new_post_main, name='new_post_main'),
    path('<slug:slug>/', views.AdDetailView.as_view(), name='ad_detail'),
    path('<slug:slug>/edit/', views.AdUpdateView.as_view(), name='ad_update'),
    path('<slug:slug>/delete/', views.AdDeleteView.as_view(), name='ad_delete'),
    
]