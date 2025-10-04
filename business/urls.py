from django.urls import path
from . import views

app_name = 'business'

urlpatterns = [
    # Business Management URLs
    path('', views.BusinessListView.as_view(), name='business_list'),
    path('create/', views.BusinessCreateView.as_view(), name='create_business'),
    path('<int:pk>/', views.business_detail, name='business_detail'),
    path('<int:pk>/update/', views.BusinessUpdateView.as_view(), name='update_business'),
    path('<int:pk>/delete/', views.delete_business, name='delete_business'),
    
    # Khata Management URLs
    path('khata/', views.KhataListView.as_view(), name='khata_list'),
    path('khata/create/', views.KhataCreateView.as_view(), name='create_khata'),
    path('khata/<int:pk>/', views.khata_detail, name='khata_detail'),
    path('khata/<int:pk>/delete/', views.delete_khata, name='delete_khata'),
    
    # AJAX URLs
    path('api/khatas/', views.get_khatas_by_business, name='get_khatas_by_business'),
    path('api/<int:pk>/stats/', views.business_stats, name='business_stats'),
]