from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Ad, MainCategory, SubCategory, PostStatus, RealEstate
from .forms import AdForm
from django.template import TemplateDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .mixins import ImageUploadMixin
from django.core.exceptions import ValidationError
import logging
from django.utils.text import slugify
from datetime import datetime

logger = logging.getLogger(__name__)

class AdListView(ListView):
    model = Ad
    template_name = 'ads/ad_list.html'
    context_object_name = 'ads'
    paginate_by = 10

    def get_queryset(self):
        published_status = PostStatus.objects.get(name='published')
        return Ad.objects.filter(status=published_status).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_categories'] = MainCategory.objects.all()
        return context

class AdDetailView(DetailView):
    model = Ad
    template_name = 'ads/ad_detail.html'

    def get_object(self):
        obj = super().get_object()
        obj.views += 1
        obj.save()
        return obj

class AdCreateView(LoginRequiredMixin, CreateView):
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class AdUpdateView(LoginRequiredMixin, UpdateView):
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'

    def get_queryset(self):
        return Ad.objects.filter(author=self.request.user)

class AdDeleteView(LoginRequiredMixin, DeleteView):
    model = Ad
    template_name = 'ads/ad_confirm_delete.html'
    success_url = reverse_lazy('ads:ad_list')

    def get_queryset(self):
        return Ad.objects.filter(author=self.request.user)

def new_post_main(request):
    """View for the new post main page."""
    return render(request, 'ads/new_post/new_post_main.html')

def new_post_base(request):
    """View for the new post base page with categories."""
    try:
        post_type = request.GET.get('type', 'buy')
        print(f"Post type: {post_type}")  # Debug info
        
        # Determine which sidebar template to use
        if post_type == 'services':
            sidebar_template = 'ads/new_post/sidebars/services_sidebar.html'
            active_page = 'professional'  # Default active page
        elif post_type == 'events':
            sidebar_template = 'ads/new_post/sidebars/events_sidebar.html'
            active_page = 'concerts'  # Default active page
        else:  # buy or rent
            sidebar_template = 'ads/new_post/sidebars/buy_rent_sidebar.html'
            active_page = 'real_estate'  # Default active page
        
        print(f"Sidebar template: {sidebar_template}")  # Debug info
        print(f"Active page: {active_page}")  # Debug info
        
        context = {
            'post_type': post_type,
            'sidebar_template': sidebar_template,
            'active_page': active_page,
            'current_step': 1,
        }
        
        return render(request, 'ads/new_post/new_post_base.html', context)
    except Exception as e:
        # Log the error
        print(f"Error in new_post_base: {str(e)}")
        # Return a 500 error page or redirect to home
        return render(request, '500.html', status=500)

def post_home1(request):
    if request.method == 'POST':
        # Save form data to session
        request.session['post_data'] = {
            'title': request.POST.get('title'),
            'listing_purpose': request.POST.get('listing_purpose'),
            'property_type': request.POST.get('property_type'),
            'price': request.POST.get('price'),
            'bedrooms': request.POST.get('bedrooms'),
            'bathrooms': request.POST.get('bathrooms'),
            'square_feet': request.POST.get('square_feet'),
            'year_built': request.POST.get('year_built'),
            'parking': request.POST.get('parking'),
            'heating': request.POST.get('heating'),
            'cooling': request.POST.get('cooling'),
            'zip_code': request.POST.get('zip_code'),
            'city': request.POST.get('city'),
            'state': request.POST.get('state'),
            'address': request.POST.get('address'),
            'hide_address': request.POST.get('hide_address') == 'on',
            'description': request.POST.get('description'),
        }
        
        # Add additional fields for rental properties
        if request.POST.get('listing_purpose') == 'rent':
            request.session['post_data'].update({
                'availability_date': request.POST.get('availability_date'),
                'lease_term': request.POST.get('lease_term'),
            })
        
        return redirect('ads:post_home2')
    
    # Load saved data if exists
    post_data = request.session.get('post_data', {})
    
    context = {
        'post_data': post_data,
        'is_buy': post_data.get('listing_purpose') == 'buy',
        'is_rent': post_data.get('listing_purpose') == 'rent'
    }
    
    return render(request, 'ads/new_post/post_home/post_home1.html', context)

def post_home2(request):
    # Check if we have data from the first step
    if 'post_data' not in request.session:
        messages.error(request, 'Please complete the first step first')
        return redirect('ads:post_home1')
    
    if request.method == 'POST':
        # If Back button is pressed, return to post_home1
        if 'back_button' in request.POST:
            return redirect('ads:post_home1')
            
        # Check if Next button is pressed
        if 'next_button_home2' not in request.POST:
            messages.error(request, 'Invalid form submission')
            return redirect('ads:post_home2')
            
        try:
            # Handle image upload
            images = ImageUploadMixin().handle_image_upload(request)
            # Save images to session, even if there are none
            request.session['post_images'] = images or []
            return redirect('ads:post_home3')
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, 'An unexpected error occurred while processing your images. Please try again.')
        
        return render(request, 'ads/new_post/post_home/post_home2.html', {
            'form': ImageUploadMixin().get_image_form()
        })
    
    return render(request, 'ads/new_post/post_home/post_home2.html', {
        'form': ImageUploadMixin().get_image_form()
    })

def post_home3(request):
    # Check if we have data from previous steps
    if 'post_data' not in request.session or 'post_images' not in request.session:
        messages.error(request, 'Please complete all previous steps first')
        return redirect('ads:post_home1')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        post_data = request.session['post_data']
        post_images = request.session['post_images']
        
        try:
            status_name = 'review' if action == 'review' else 'draft'
            status = PostStatus.objects.get(name=status_name)
            
            # Get categories for real estate
            main_category = MainCategory.objects.get(slug='Sell-rent')
            
            # Always use real-estate subcategory
            sub_category = SubCategory.objects.get(slug='real-estate')
            
            # Generate unique slug
            base_slug = slugify(post_data.get('title', ''))
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique_slug = f"{base_slug}-{timestamp}"
            
            # Convert empty values to None for numeric fields
            def get_int_or_none(value):
                return int(value) if value and value.strip() else None
            
            # Create real estate object
            real_estate = RealEstate(
                author=request.user,
                status=status,
                title=post_data.get('title', ''),
                description=post_data.get('description', ''),
                listing_purpose=post_data.get('listing_purpose'),
                property_type=post_data.get('property_type'),
                price=get_int_or_none(post_data.get('price', '')),
                bedrooms=get_int_or_none(post_data.get('bedrooms', '')),
                bathrooms=get_int_or_none(post_data.get('bathrooms', '')),
                square_feet=get_int_or_none(post_data.get('square_feet', '')),
                year_built=get_int_or_none(post_data.get('year_built', '')),
                parking=post_data.get('parking'),
                heating=post_data.get('heating'),
                cooling=post_data.get('cooling'),
                address=post_data.get('address'),
                city=post_data.get('city'),
                state=post_data.get('state'),
                zip_code=post_data.get('zip_code'),
                hide_address=post_data.get('hide_address', False),
                main_category=main_category,
                sub_category=sub_category,
                slug=unique_slug
            )
            
            if post_data.get('listing_purpose') == 'rent':
                real_estate.availability_date = post_data.get('availability_date')
                real_estate.lease_term = post_data.get('lease_term')
            
            real_estate.save()
            
            # Save images
            for image_data in post_images:
                real_estate.images.create(image=image_data['path'])
            
            # Clear session data
            request.session.pop('post_data', None)
            request.session.pop('post_images', None)
            
            if action == 'review':
                messages.success(request, 'Your listing has been submitted for review!')
            else:
                messages.success(request, 'Your listing has been saved as draft.')
            
            return redirect('ads:my_listings')
            
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('ads:post_home1')
    
    # GET request - show preview page
    post_data = request.session.get('post_data', {})
    post_images = request.session.get('post_images', [])
    
    context = {
        'title': post_data.get('title'),
        'listing_purpose': post_data.get('listing_purpose'),
        'property_type': post_data.get('property_type'),
        'price': post_data.get('price'),
        'bedrooms': post_data.get('bedrooms'),
        'bathrooms': post_data.get('bathrooms'),
        'square_feet': post_data.get('square_feet'),
        'year_built': post_data.get('year_built'),
        'parking': post_data.get('parking'),
        'heating': post_data.get('heating'),
        'cooling': post_data.get('cooling'),
        'address': post_data.get('address'),
        'city': post_data.get('city'),
        'state': post_data.get('state'),
        'zip_code': post_data.get('zip_code'),
        'hide_address': post_data.get('hide_address'),
        'description': post_data.get('description'),
        'images': post_images
    }
    
    return render(request, 'ads/new_post/post_home/post_home3.html', context)

def load_sidebar(request):
    """View for loading sidebar content via AJAX"""
    post_type = request.GET.get('type', 'buy')
    category = request.GET.get('category', '')
    
    # Determine which sidebar template to use
    if post_type == 'services':
        template = 'ads/new_post/sidebars/services_sidebar.html'
        active_page = category
    elif post_type == 'events':
        template = 'ads/new_post/sidebars/events_sidebar.html'
        active_page = category
    else:  # buy or rent
        template = 'ads/new_post/sidebars/buy_rent_sidebar.html'
        active_page = 'real_estate'
    
    return render(request, template, {
        'active_page': active_page,
        'post_type': post_type
    })

@require_GET
def get_subcategories(request):
    """API endpoint to get subcategories for a main category."""
    main_category_id = request.GET.get('main_category')
    if main_category_id:
        subcategories = SubCategory.objects.filter(main_category_id=main_category_id)
        data = [{'id': sub.id, 'name': sub.name} for sub in subcategories]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

def post_step(request, post_type, step):
    """View for loading step content."""
    try:
        print(f"Post type: {post_type}, Step: {step}")  # Debug info
        
        # Определяем шаблон в зависимости от типа поста и шага
        if post_type == 'buy':
            template = 'ads/new_post/post_home/post_home1.html'
        elif post_type == 'services':
            template = 'ads/new_post/post_services/post_services1.html'
        elif post_type == 'events':
            template = 'ads/new_post/post_events/post_events1.html'
        else:
            print(f"Invalid post type: {post_type}")  # Debug info
            return JsonResponse({'error': 'Invalid post type'}, status=400)

        print(f"Using template: {template}")  # Debug info

        context = {
            'post_type': post_type,
            'current_step': step,
            'sidebar_template': f'ads/new_post/sidebars/{post_type}_sidebar.html',
            'active_page': 'real_estate' if post_type == 'buy' else 'professional'
        }
        
        print(f"Context: {context}")  # Debug info
        
        # Проверяем существование шаблона
        try:
            return render(request, template, context)
        except TemplateDoesNotExist:
            print(f"Template not found: {template}")  # Debug info
            return JsonResponse({'error': 'Template not found'}, status=404)
            
    except Exception as e:
        print(f"Error in post_step: {str(e)}")  # Debug info
        return JsonResponse({'error': str(e)}, status=500)

def buy_rent_page(request):
    """View for the buy/rent page with sidebar."""
    return render(request, 'ads/new_post/sidebars/buy_rent_sidebar.html', {
        'post_type': 'buy',
        'active_page': 'real_estate'
    })

def post_vehicles_main(request):
    """View for the vehicles main page"""
    return render(request, 'ads/post_vehicles/post_vehicles_main.html')

def post_vehicles1(request):
    """View for the first step of vehicle posting form."""
    if request.method == 'POST':
        # Save form data to session
        request.session['vehicle_data'] = {
            'title': request.POST.get('title'),
            'listing_purpose': request.POST.get('listing_purpose'),
            'vehicle_type': request.POST.get('vehicle_type'),
            'make': request.POST.get('make'),
            'model': request.POST.get('model'),
            'year': request.POST.get('year'),
            'price': request.POST.get('price'),
            'zip_code': request.POST.get('zip_code'),
            'city': request.POST.get('city'),
            'state': request.POST.get('state'),
            'additional_details': request.POST.get('additional_details'),
            'description': request.POST.get('description'),
        }
        return redirect('ads:post_vehicles2')
    
    # Load saved data if exists
    vehicle_data = request.session.get('vehicle_data', {})
    vehicle_type = vehicle_data.get('vehicle_type', '')
    
    # Add boolean flags for listing purpose and vehicle type
    context = {
        'vehicle_data': vehicle_data,
        'is_buy': vehicle_data.get('listing_purpose') == 'buy',
        'is_rent': vehicle_data.get('listing_purpose') == 'rent',
        'is_sedan': vehicle_type == 'sedan',
        'is_suv': vehicle_type == 'suv',
        'is_truck': vehicle_type == 'truck',
        'is_van': vehicle_type == 'van',
        'is_coupe': vehicle_type == 'coupe',
        'is_wagon': vehicle_type == 'wagon',
        'is_convertible': vehicle_type == 'convertible'
    }
    
    return render(request, 'ads/post_vehicles/post_vehicles1.html', context)

def post_vehicles2(request):
    """Second step of vehicle posting form for image upload."""
    # Проверяем, есть ли данные из первого шага
    if 'vehicle_data' not in request.session:
        messages.error(request, 'Please complete the first step first')
        return redirect('ads:post_vehicles1')
    
    if request.method == 'POST':
        # Если нажата кнопка Back, возвращаемся на post_vehicles1
        if 'back_button' in request.POST:
            return redirect('ads:post_vehicles1')
            
        # Проверяем, что нажата кнопка Next
        if 'next_button_vehicles2' not in request.POST:
            messages.error(request, 'Invalid form submission')
            return redirect('ads:post_vehicles2')
            
        try:
            # Обработка загрузки изображений
            images = ImageUploadMixin().handle_image_upload(request)
            # Сохраняем изображения в сессии
            request.session['vehicle_images'] = images or []
            logger.info(f"Successfully processed {len(images)} images")
            return redirect('ads:post_vehicles3')
        except ValidationError as e:
            logger.error(f"Validation error in post_vehicles2: {str(e)}")
            messages.error(request, str(e))
        except Exception as e:
            logger.error(f"Unexpected error in post_vehicles2: {str(e)}")
            messages.error(request, 'An unexpected error occurred while processing your images. Please try again.')
        
        return render(request, 'ads/post_vehicles/post_vehicles2.html', {
            'form': ImageUploadMixin().get_image_form()
        })
    
    return render(request, 'ads/post_vehicles/post_vehicles2.html', {
        'form': ImageUploadMixin().get_image_form()
    })

def post_vehicles3(request):
    """Third step of vehicle posting form for review."""
    # Проверяем, есть ли данные из предыдущих шагов
    if 'vehicle_data' not in request.session or 'vehicle_images' not in request.session:
        messages.error(request, 'Please complete all previous steps first')
        return redirect('ads:post_vehicles1')
    
    if request.method == 'POST':
        # Если нажата кнопка Back, возвращаемся на post_vehicles2
        if 'back_button' in request.POST:
            return redirect('ads:post_vehicles2')
            
        # Если нажата кнопка Submit
        if 'submit_button' in request.POST:
            try:
                # Создаем новое объявление
                vehicle_data = request.session['vehicle_data']
                vehicle_images = request.session['vehicle_images']
                
                # TODO: Создать и сохранить объявление в базе данных
                # После успешного создания очищаем данные сессии
                request.session.pop('vehicle_data', None)
                request.session.pop('vehicle_images', None)
                
                messages.success(request, 'Your vehicle listing has been successfully created!')
                return redirect('ads:ad_list')
            except Exception as e:
                logger.error(f"Error creating vehicle listing: {str(e)}")
                messages.error(request, 'An error occurred while creating your listing. Please try again.')
    
    context = {
        'form_data': request.session['vehicle_data'],
        'images': request.session['vehicle_images']
    }
    
    return render(request, 'ads/post_vehicles/post_vehicles3.html', context)
