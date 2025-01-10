
from django.contrib import admin
from django.urls import path
from .views import DashboardView, Roznamcha, AccountsView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('roznamcha/', Roznamcha.as_view(), name='roznamcha'),
    path('accounts/', AccountsView.as_view(), name='accounts'),
]
