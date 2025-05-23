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
    post_type = request.GET.get('type', 'buy')
    return render(request, 'ads/new_post/new_post_base.html', {
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
