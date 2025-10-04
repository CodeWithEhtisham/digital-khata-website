from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('', views.dashboard, name='dashboard'),
    path('sign-up/', views.SignUpView.as_view(), name='sign-up'),
    path('sign-in/', views.SignInView.as_view(), name='sign-in'),
    path('sign-out/', views.sign_out, name='sign-out'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.UserUpdateView.as_view(), name='update-profile'),
    path('profile/change-password/', views.CustomPasswordChangeView.as_view(), name='change-password'),
    
    # Account Management URLs
    path('accounts/', views.AccountListView.as_view(), name='account_list'),
    path('accounts/create/', views.AccountCreateView.as_view(), name='create_account'),
    path('accounts/<int:pk>/', views.AccountDetailView.as_view(), name='account_detail'),
    path('accounts/<int:pk>/update/', views.AccountUpdateView.as_view(), name='update_account'),
    
    # Roznamcha (Ledger) URLs
    path('roznamcha/', views.RoznamchaListView.as_view(), name='roznamcha_list'),
    path('roznamcha/create/', views.RoznamchaCreateView.as_view(), name='create_roznamcha'),
    path('roznamcha/<int:pk>/update/', views.RoznamchaUpdateView.as_view(), name='update_roznamcha'),
]
