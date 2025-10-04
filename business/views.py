from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from accounts.models import Business, Khata
from .forms import BusinessForm, KhataForm

class BusinessCreateView(LoginRequiredMixin, CreateView):
    """Create new business - matching create_business.py functionality"""
    model = Business
    form_class = BusinessForm
    template_name = 'business/create_business.html'
    success_url = reverse_lazy('business:business_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Business created successfully!')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class BusinessUpdateView(LoginRequiredMixin, UpdateView):
    """Update business details - matching update_business_details.py functionality"""
    model = Business
    form_class = BusinessForm
    template_name = 'business/update_business.html'
    success_url = reverse_lazy('business:business_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Business details updated successfully!')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class BusinessListView(LoginRequiredMixin, ListView):
    """List all businesses"""
    model = Business
    template_name = 'business/business_list.html'
    context_object_name = 'businesses'
    paginate_by = 10


@login_required
def business_detail(request, pk):
    """Business detail view with khatas and statistics"""
    business = get_object_or_404(Business, pk=pk)
    khatas = Khata.objects.filter(business=business)
    
    # Calculate statistics
    total_khatas = khatas.count()
    total_accounts = sum(khata.accounts.count() for khata in khatas)
    
    context = {
        'business': business,
        'khatas': khatas,
        'total_khatas': total_khatas,
        'total_accounts': total_accounts,
    }
    return render(request, 'business/business_detail.html', context)


class KhataCreateView(LoginRequiredMixin, CreateView):
    """Create new khata - matching khata_details.py functionality"""
    model = Khata
    form_class = KhataForm
    template_name = 'business/create_khata.html'
    
    def get_success_url(self):
        return reverse_lazy('business:business_detail', kwargs={'pk': self.object.business.pk})
    
    def form_valid(self, form):
        # Associate khata with business from URL or form
        business_id = self.request.GET.get('business_id')
        if business_id:
            form.instance.business = get_object_or_404(Business, pk=business_id)
        response = super().form_valid(form)
        messages.success(self.request, f'Khata "{self.object.khata_name}" created successfully!')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        business_id = self.request.GET.get('business_id')
        if business_id:
            context['business'] = get_object_or_404(Business, pk=business_id)
        return context


class KhataListView(LoginRequiredMixin, ListView):
    """List all khatas"""
    model = Khata
    template_name = 'business/khata_list.html'
    context_object_name = 'khatas'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Khata.objects.all()
        business_id = self.request.GET.get('business')
        if business_id:
            queryset = queryset.filter(business_id=business_id)
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['businesses'] = Business.objects.all()
        context['selected_business'] = self.request.GET.get('business')
        return context


@login_required
def khata_detail(request, pk):
    """Khata detail view with accounts and statistics"""
    khata = get_object_or_404(Khata, pk=pk)
    accounts = khata.accounts.all()
    
    # Calculate account statistics
    total_accounts = accounts.count()
    total_payable = sum(acc.balance for acc in accounts if acc.balance_type == 'CREDIT')
    total_receivable = sum(acc.balance for acc in accounts if acc.balance_type == 'DEBIT')
    net_balance = total_payable - total_receivable
    
    # Get recent roznamcha entries
    recent_entries = khata.roznamcha_entries.all()[:10]
    
    context = {
        'khata': khata,
        'accounts': accounts,
        'total_accounts': total_accounts,
        'total_payable': total_payable,
        'total_receivable': total_receivable,
        'net_balance': net_balance,
        'recent_entries': recent_entries,
    }
    return render(request, 'business/khata_detail.html', context)


@login_required
def delete_business(request, pk):
    """Delete business with confirmation"""
    business = get_object_or_404(Business, pk=pk)
    
    if request.method == 'POST':
        business_name = business.business_name
        business.delete()
        messages.success(request, f'Business "{business_name}" deleted successfully!')
        return redirect('business:business_list')
    
    return render(request, 'business/confirm_delete.html', {'business': business})


@login_required
def delete_khata(request, pk):
    """Delete khata with confirmation"""
    khata = get_object_or_404(Khata, pk=pk)
    business_pk = khata.business.pk
    
    if request.method == 'POST':
        khata_name = khata.khata_name
        khata.delete()
        messages.success(request, f'Khata "{khata_name}" deleted successfully!')
        return redirect('business:business_detail', pk=business_pk)
    
    return render(request, 'business/confirm_delete_khata.html', {'khata': khata})


# AJAX Views
@login_required
def get_khatas_by_business(request):
    """Get khatas for a specific business (AJAX)"""
    business_id = request.GET.get('business_id')
    if business_id:
        khatas = Khata.objects.filter(business_id=business_id).values('id', 'khata_name')
        return JsonResponse({'khatas': list(khatas)})
    return JsonResponse({'khatas': []})


@login_required
def business_stats(request, pk):
    """Get business statistics (AJAX)"""
    business = get_object_or_404(Business, pk=pk)
    
    # Calculate comprehensive statistics
    khatas = business.khatas.all()
    total_khatas = khatas.count()
    total_accounts = sum(khata.accounts.count() for khata in khatas)
    
    # Calculate financial statistics
    total_cash_in = 0
    total_cash_out = 0
    for khata in khatas:
        entries = khata.roznamcha_entries.all()
        total_cash_in += sum(entry.cash_in for entry in entries)
        total_cash_out += sum(entry.cash_out for entry in entries)
    
    stats = {
        'total_khatas': total_khatas,
        'total_accounts': total_accounts,
        'total_cash_in': float(total_cash_in),
        'total_cash_out': float(total_cash_out),
        'net_balance': float(total_cash_in - total_cash_out),
    }
    
    return JsonResponse(stats)
