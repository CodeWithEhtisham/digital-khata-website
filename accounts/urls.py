
from django.contrib import admin
from django.urls import path
from .views import SignInView
urlpatterns = [
    path('', SignInView.as_view(), name='signin'),
]
