
from django.contrib import admin
from django.urls import path
from .views import SignInView,SignUpView, ProfileView,SignOutView
urlpatterns = [
    path('sign-in/', SignInView.as_view(), name='signin'),
    path('sign-up/', SignUpView.as_view(), name='signup'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('sign-out/', SignOutView.as_view(), name='signout'),

]
 