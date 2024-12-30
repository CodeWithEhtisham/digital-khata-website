from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.
class SignInView(TemplateView):
    template_name = "accounts/sign-up.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
