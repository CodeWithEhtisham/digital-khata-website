from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.
class DashboardView(TemplateView):
    template_name = "rozmancha/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'DashboardView'
        return context
    
class Roznamcha(TemplateView):
    template_name = "rozmancha/roznamcha.html"
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
class AccountsView(TemplateView):
    template_name = "rozmancha/accounts.html"
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)