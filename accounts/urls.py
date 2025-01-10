
from django.contrib import admin
from django.urls import path
from .views import SignInView,SignUpView
urlpatterns = [
    path('sign-in/', SignInView.as_view(), name='signin'),
    path('sign-up/', SignUpView.as_view(), name='signup'),
]
