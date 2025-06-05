from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.
class SignInView(TemplateView):
    template_name = "accounts/sign-in.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class SignUpView(TemplateView):
    template_name = "accounts/sign-up.html"
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
class ProfileView(TemplateView):
    template_name = "accounts/profile.html"
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name) 
    
class SignOutView(TemplateView):
    template_name = "accounts/sign-in.html"
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)