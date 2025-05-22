from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Ad, Category

class AdListView(ListView):
    model = Ad
    template_name = 'ads/ad_list.html'
    context_object_name = 'ads'
    paginate_by = 10

    def get_queryset(self):
        return Ad.objects.filter(status='published')

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
    template_name = 'ads/ad_form.html'
    fields = ['title', 'description', 'price', 'category']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class AdUpdateView(LoginRequiredMixin, UpdateView):
    model = Ad
    template_name = 'ads/ad_form.html'
    fields = ['title', 'description', 'price', 'category']

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
