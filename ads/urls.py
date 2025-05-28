from django.urls import path
from . import views

app_name = 'ads'

urlpatterns = [
    path('', views.AdListView.as_view(), name='ad_list'),
    path('create/', views.AdCreateView.as_view(), name='ad_create'),
    path('new-post/', views.new_post_main, name='new_post_main'),
    path('new-post/base/', views.new_post_base, name='new_post_base'),
    path('new-post/load-sidebar/', views.load_sidebar, name='load_sidebar'),
    path('new-post/buy-rent/', views.buy_rent_page, name='buy_rent_page'),
    path('new-post/vehicles/', views.post_vehicles_main, name='post_vehicles_main'),
    path('post/<str:post_type>/step/<int:step>/', views.post_step, name='post_step'),
    path('api/subcategories/', views.get_subcategories, name='get_subcategories'),
    
    # Multi-step form URLs
    path('post/home/step1/', views.post_home1, name='post_home1'),
    path('post/home/step2/', views.post_home2, name='post_home2'),
    path('post/home/step3/', views.post_home3, name='post_home3'),
    
    # Ad detail URLs
    path('<slug:slug>/', views.AdDetailView.as_view(), name='ad_detail'),
    path('<slug:slug>/edit/', views.AdUpdateView.as_view(), name='ad_update'),
    path('<slug:slug>/delete/', views.AdDeleteView.as_view(), name='ad_delete'),
]