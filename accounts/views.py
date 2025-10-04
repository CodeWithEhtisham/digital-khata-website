from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView
from django.http import JsonResponse
from django.db.models import Q, Sum
from decimal import Decimal
from .models import User, Account, Roznamcha, Business, Khata
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, UserUpdateForm, 
    CustomPasswordChangeForm, AccountForm, RoznamchaForm
)

# User Authentication Views
class SignUpView(CreateView):
    """User registration - matching create_user.py functionality"""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/sign-up.html'
    success_url = reverse_lazy('accounts:profile')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f'Welcome {self.object.name}! Your account has been created.')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class SignInView(LoginView):
    """User login - matching login_page.py functionality"""
    form_class = CustomAuthenticationForm
    template_name = 'accounts/sign-in.html'
    success_url = reverse_lazy('accounts:dashboard')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Don't show success message on sign-in page, just redirect
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view"""
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        
        # Get user statistics
        businesses = Business.objects.all().count()
        khatas = Khata.objects.all().count()
        accounts = Account.objects.all().count()
        
        context.update({
            'total_businesses': businesses,
            'total_khatas': khatas,
            'total_accounts': accounts,
        })
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """Update user details - matching update_user_details.py functionality"""
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/update_profile.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your profile has been updated successfully!')
        return response


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Change password - matching update_password.py functionality"""
    form_class = CustomPasswordChangeForm
    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('accounts:profile')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your password has been changed successfully!')
        return response


@login_required
def sign_out(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been signed out successfully.')
    return redirect('accounts:sign-in')


@login_required
def dashboard(request):
    """Main dashboard - matching main_window.py home functionality"""
    # Ensure user has a business assigned
    if not request.user.business:
        messages.error(request, 'No business is associated with your account. Please contact the administrator.')
        return redirect('accounts:profile')
    
    user_business = request.user.business
    
    # Get business-specific statistics
    total_businesses = 1  # Current user's business only
    total_khatas = Khata.objects.filter(business=user_business).count()
    total_accounts = Account.objects.filter(business=user_business).count()
    
    # Get recent activities for this business only
    recent_accounts = Account.objects.filter(business=user_business).order_by('-created_at')[:5]
    recent_entries = Roznamcha.objects.filter(
        khata__business=user_business
    ).order_by('-created_at')[:10]
    
    # Calculate financial overview for this business only
    business_entries = Roznamcha.objects.filter(khata__business=user_business)
    total_cash_in = business_entries.aggregate(total=Sum('cash_in'))['total'] or Decimal('0.00')
    total_cash_out = business_entries.aggregate(total=Sum('cash_out'))['total'] or Decimal('0.00')
    net_balance = total_cash_in - total_cash_out
    
    context = {
        'current_business': user_business,
        'total_businesses': total_businesses,
        'total_khatas': total_khatas,
        'total_accounts': total_accounts,
        'recent_accounts': recent_accounts,
        'recent_entries': recent_entries,
        'total_cash_in': total_cash_in,
        'total_cash_out': total_cash_out,
        'net_balance': net_balance,
    }
    return render(request, 'accounts/dashboard.html', context)


# Account Management Views
class AccountCreateView(LoginRequiredMixin, CreateView):
    """Create new account - matching add_accounts.py functionality"""
    model = Account
    form_class = AccountForm
    template_name = 'accounts/create_account.html'
    success_url = reverse_lazy('accounts:account_list')
    
    def get_form_kwargs(self):
        """Ensure form is initialized without instance to prevent preloaded values"""
        kwargs = super().get_form_kwargs()
        # Remove instance to prevent preloaded default values
        if 'instance' in kwargs:
            kwargs.pop('instance')
        # Add business context to form
        kwargs['business'] = self.request.user.business
        return kwargs
    
    def form_valid(self, form):
        # Ensure the account belongs to the current user's business
        form.instance.business = self.request.user.business
        response = super().form_valid(form)
        messages.success(self.request, f'Account "{self.object.name}" created successfully!')
        return response


class AccountUpdateView(LoginRequiredMixin, UpdateView):
    """Update account - matching update_accounts.py functionality"""
    model = Account
    form_class = AccountForm
    template_name = 'accounts/update_account.html'
    success_url = reverse_lazy('accounts:account_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Account "{self.object.name}" updated successfully!')
        return response


class AccountListView(LoginRequiredMixin, ListView):
    """List all accounts - matching main_window.py accounts table functionality"""
    model = Account
    template_name = 'accounts/account_list.html'
    context_object_name = 'accounts'
    paginate_by = 20
    
    def get_queryset(self):
        # Start with business-filtered queryset
        queryset = Account.objects.filter(business=self.request.user.business)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(address__icontains=search_query)
            )
        
        # Filter by khata (only khatas from current business)
        khata_id = self.request.GET.get('khata')
        if khata_id:
            queryset = queryset.filter(
                khata_id=khata_id,
                khata__business=self.request.user.business
            )
            
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        accounts = self.get_queryset()
        
        # Calculate statistics
        total_accounts = accounts.count()
        total_payable = accounts.filter(balance_type='CREDIT').aggregate(
            total=Sum('balance'))['total'] or Decimal('0.00')
        total_receivable = accounts.filter(balance_type='DEBIT').aggregate(
            total=Sum('balance'))['total'] or Decimal('0.00')
        
        context.update({
            'total_accounts': total_accounts,
            'total_payable': total_payable,
            'total_receivable': total_receivable,
            'net_balance': total_payable - total_receivable,
            'khatas': Khata.objects.filter(business=self.request.user.business),
            'selected_khata': self.request.GET.get('khata', ''),
            'search_query': self.request.GET.get('search', ''),
        })
        return context


class AccountDetailView(LoginRequiredMixin, DetailView):
    """Account detail view - matching account_details.py functionality"""
    model = Account
    template_name = 'accounts/account_detail.html'
    context_object_name = 'account'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account = self.object
        
        # Get account's roznamcha entries
        entries = account.roznamcha_entries.all().order_by('-date', '-id')
        
        # Calculate running balance and statistics
        total_cash_in = entries.aggregate(total=Sum('cash_in'))['total'] or Decimal('0.00')
        total_cash_out = entries.aggregate(total=Sum('cash_out'))['total'] or Decimal('0.00')
        
        context.update({
            'entries': entries,
            'total_cash_in': total_cash_in,
            'total_cash_out': total_cash_out,
            'current_balance': account.balance + (total_cash_in - total_cash_out),
        })
        return context


# Roznamcha (Ledger) Views  
class RoznamchaCreateView(LoginRequiredMixin, CreateView):
    """Create roznamcha entry - matching add_roznamcha.py functionality"""
    model = Roznamcha
    form_class = RoznamchaForm
    template_name = 'accounts/create_roznamcha.html'
    success_url = reverse_lazy('accounts:roznamcha_list')
    
    def get_form_kwargs(self):
        """Ensure form is initialized without instance to prevent preloaded values"""
        kwargs = super().get_form_kwargs()
        # Remove instance to prevent preloaded default values
        if 'instance' in kwargs:
            kwargs.pop('instance')
        # Add business context to form
        kwargs['business'] = self.request.user.business
        return kwargs
    
    def form_valid(self, form):
        # Calculate remaining balance
        entry = form.instance
        account = entry.account
        
        # Get current balance from previous entries
        previous_entries = account.roznamcha_entries.all()
        current_balance = account.balance
        
        for prev_entry in previous_entries:
            current_balance += prev_entry.cash_in - prev_entry.cash_out
            
        # Update remaining balance
        if entry.cash_in:
            entry.remaining = current_balance + entry.cash_in
        else:
            entry.remaining = current_balance - entry.cash_out
            
        entry.accounts_remaining = entry.remaining
        
        response = super().form_valid(form)
        messages.success(self.request, 'Roznamcha entry created successfully!')
        return response


class RoznamchaUpdateView(LoginRequiredMixin, UpdateView):
    """Update roznamcha entry - matching update_roznamcha.py functionality"""
    model = Roznamcha
    form_class = RoznamchaForm
    template_name = 'accounts/update_roznamcha.html'
    success_url = reverse_lazy('accounts:roznamcha_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Roznamcha entry updated successfully!')
        return response


class RoznamchaListView(LoginRequiredMixin, ListView):
    """List roznamcha entries - matching main_window.py roznamcha table functionality"""
    model = Roznamcha
    template_name = 'accounts/roznamcha_list.html'
    context_object_name = 'entries'
    paginate_by = 50
    
    def get_queryset(self):
        # Start with business-filtered queryset
        queryset = Roznamcha.objects.filter(khata__business=self.request.user.business)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(account__name__icontains=search_query) |
                Q(references__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Date range filtering
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
            
        # Filter by khata
        khata_id = self.request.GET.get('khata')
        if khata_id:
            queryset = queryset.filter(khata_id=khata_id)
            
        return queryset.order_by('-date', '-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entries = self.get_queryset()
        
        # Calculate statistics
        total_cash_in = entries.aggregate(total=Sum('cash_in'))['total'] or Decimal('0.00')
        total_cash_out = entries.aggregate(total=Sum('cash_out'))['total'] or Decimal('0.00')
        
        context.update({
            'total_cash_in': total_cash_in,
            'total_cash_out': total_cash_out,
            'remaining_balance': total_cash_in - total_cash_out,
            'khatas': Khata.objects.all(),
            'selected_khata': self.request.GET.get('khata', ''),
            'search_query': self.request.GET.get('search', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
        })
        return context
