from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Ad, MainCategory, SubCategory
from .forms import AdForm

class AdListView(ListView):
    model = Ad
    template_name = 'ads/ad_list.html'
    context_object_name = 'ads'
    paginate_by = 10

    def get_queryset(self):
        return Ad.objects.filter(status='published')

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
        
        context = {
            'post_type': post_type,
            'sidebar_template': sidebar_template,
            'active_page': active_page,
        }
        
        return render(request, 'ads/new_post/new_post_base.html', context)
    except Exception as e:
        # Log the error
        print(f"Error in new_post_base: {str(e)}")
        # Return a 500 error page or redirect to home
        return render(request, '500.html', status=500)

def post_home1(request):
    post_type = request.GET.get('type', 'buy')
    category = request.GET.get('category', '')
    
    # Determine which sidebar template to use
    if post_type == 'services':
        sidebar_template = 'ads/new_post/sidebars/services_sidebar.html'
        active_page = category
    elif post_type == 'events':
        sidebar_template = 'ads/new_post/sidebars/events_sidebar.html'
        active_page = category
    else:  # buy or rent
        sidebar_template = 'ads/new_post/sidebars/buy_rent_sidebar.html'
        active_page = 'real_estate'
    
    context = {
        'post_type': post_type,
        'sidebar_template': sidebar_template,
        'active_page': active_page,
    }
    
    return render(request, 'ads/new_post/post_home/post_home1.html', context)

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
