from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Ad, MainCategory, SubCategory, PostStatus
from .forms import AdForm
from django.template import TemplateDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .mixins import ImageUploadMixin
from django.core.exceptions import ValidationError
import logging

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
        # Сохраняем данные в сессии
        request.session['post_data'] = {
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
        
        # Если это аренда, добавляем дополнительные поля
        if request.POST.get('listing_purpose') == 'rent':
            request.session['post_data'].update({
                'availability_date': request.POST.get('availability_date'),
                'lease_term': request.POST.get('lease_term'),
            })
        
        return redirect('ads:post_home2')
    
    # Если есть сохраненные данные, загружаем их
    post_data = request.session.get('post_data', {})
    return render(request, 'ads/new_post/post_home/post_home1.html', {'post_data': post_data})

def post_home2(request):
    # Проверяем, есть ли данные из первого шага
    if 'post_data' not in request.session:
        messages.error(request, 'Please complete the first step first')
        return redirect('ads:post_home1')
    
    if request.method == 'POST':
        try:
            # Обработка загрузки изображений
            images = ImageUploadMixin().handle_image_upload(request)
            if images:
                request.session['post_images'] = images
                logger.info(f"Successfully processed {len(images)} images")
                return redirect('ads:post_home3')
            else:
                messages.warning(request, 'No images were uploaded')
                return render(request, 'ads/new_post/post_home/post_home2.html', {
                    'form': ImageUploadMixin().get_image_form()
                })
        except ValidationError as e:
            logger.error(f"Validation error in post_home2: {str(e)}")
            messages.error(request, str(e))
        except Exception as e:
            logger.error(f"Unexpected error in post_home2: {str(e)}")
            messages.error(request, 'An unexpected error occurred while processing your images. Please try again.')
        
        return render(request, 'ads/new_post/post_home/post_home2.html', {
            'form': ImageUploadMixin().get_image_form()
        })
    
    return render(request, 'ads/new_post/post_home/post_home2.html', {
        'form': ImageUploadMixin().get_image_form()
    })

def post_home3(request):
    # Проверяем, есть ли данные из предыдущих шагов
    if 'post_data' not in request.session or 'post_images' not in request.session:
        messages.error(request, 'Please complete all previous steps first')
        return redirect('ads:post_home1')
    
    if request.method == 'POST':
        # Здесь будет логика сохранения объявления в базу данных
        # После успешного сохранения очищаем сессию
        request.session.pop('post_data', None)
        request.session.pop('post_images', None)
        messages.success(request, 'Your listing has been successfully posted!')
        return redirect('ads:ad_list')  # Редирект на список объявлений
    
    # Подготавливаем данные для отображения
    context = {
        **request.session['post_data'],
        'images': [{'url': f'/media/{image["path"]}'} for image in request.session['post_images']]
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
