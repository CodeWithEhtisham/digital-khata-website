"""
Advanced Digital Khata Views
Handles notifications, payments, reports, and customer portal features
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q, Sum
from django.core.paginator import Paginator
import json
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    Business, Account, Roznamcha, Notification, NotificationTemplate,
    Payment, PaymentMethod, BusinessReport, CustomerPortalAccess
)
from .services import (
    NotificationService, PaymentIntegrationService,
    BusinessAnalyticsService, CustomerPortalService
)


# ============== SMART NOTIFICATIONS ===============

class NotificationListView(LoginRequiredMixin, ListView):
    """View all notifications for the business"""
    model = Notification
    template_name = 'accounts/notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return Notification.objects.filter(
            business=self.request.user.business
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Notification statistics
        notifications = self.get_queryset()
        context.update({
            'total_notifications': notifications.count(),
            'sent_notifications': notifications.filter(status='SENT').count(),
            'pending_notifications': notifications.filter(status='PENDING').count(),
            'failed_notifications': notifications.filter(status='FAILED').count(),
        })
        return context


@login_required
def send_payment_reminders(request):
    """Manually trigger payment reminders"""
    if request.method == 'POST':
        business = request.user.business
        NotificationService.schedule_payment_reminders(business)
        messages.success(request, 'Payment reminders have been scheduled!')
    
    return redirect('accounts:notifications')


class NotificationTemplateListView(LoginRequiredMixin, ListView):
    """Manage notification templates"""
    model = NotificationTemplate
    template_name = 'accounts/notifications/template_list.html'
    context_object_name = 'templates'
    
    def get_queryset(self):
        return NotificationTemplate.objects.filter(
            business=self.request.user.business
        ).order_by('template_type', 'channel')


# ============== PAYMENT INTEGRATION ===============

class PaymentMethodListView(LoginRequiredMixin, ListView):
    """Manage payment methods"""
    model = PaymentMethod
    template_name = 'accounts/payments/payment_methods.html'
    context_object_name = 'payment_methods'
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(
            business=self.request.user.business
        ).order_by('method_type')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Generate RAAST QR if enabled
        business = self.request.user.business
        if business.enable_raast:
            context['raast_qr_data'] = PaymentIntegrationService.generate_raast_qr(business)
        
        return context


class PaymentListView(LoginRequiredMixin, ListView):
    """View payment transactions"""
    model = Payment
    template_name = 'accounts/payments/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Payment.objects.filter(business=self.request.user.business)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by payment method
        method = self.request.GET.get('method')
        if method:
            queryset = queryset.filter(payment_method__method_type=method)
        
        return queryset.order_by('-payment_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Payment statistics
        payments = Payment.objects.filter(business=self.request.user.business)
        total_amount = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        context.update({
            'total_payments': payments.count(),
            'total_amount': total_amount,
            'completed_payments': payments.filter(status='COMPLETED').count(),
            'pending_payments': payments.filter(status='PENDING').count(),
            'payment_methods': PaymentMethod.objects.filter(
                business=self.request.user.business, is_active=True
            )
        })
        return context


# ============== BUSINESS REPORTS & ANALYTICS ===============

class ReportsView(LoginRequiredMixin, TemplateView):
    """Business reports dashboard"""
    template_name = 'accounts/reports/reports_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        business = self.request.user.business
        
        # Generate today's summary
        today_report = BusinessAnalyticsService.generate_daily_summary(business)
        
        # Get customer aging report
        aging_data = BusinessAnalyticsService.get_customer_aging_report(business)
        
        # Recent reports
        recent_reports = BusinessReport.objects.filter(
            business=business
        ).order_by('-generated_at')[:5]
        
        context.update({
            'today_report': today_report,
            'aging_data': aging_data,
            'recent_reports': recent_reports,
        })
        return context


@login_required
def generate_report(request):
    """Generate specific business report"""
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        business = request.user.business
        
        if report_type == 'DAILY_SUMMARY':
            date = datetime.strptime(start_date, '%Y-%m-%d').date()
            report = BusinessAnalyticsService.generate_daily_summary(business, date)
            messages.success(request, f'Daily summary for {date} generated successfully!')
        
        return redirect('accounts:reports')
    
    return redirect('accounts:reports')


@login_required
def customer_aging_report_json(request):
    """Get customer aging report as JSON for charts"""
    business = request.user.business
    aging_data = BusinessAnalyticsService.get_customer_aging_report(business)
    
    return JsonResponse({
        'aging_data': aging_data
    })


# ============== CUSTOMER PORTAL ===============

def customer_portal_login(request, token):
    """Customer portal access via secure token"""
    try:
        account = Account.objects.get(
            portal_access_token=token,
            portal_access_enabled=True
        )
        
        # Log access
        CustomerPortalAccess.objects.create(
            account=account,
            access_token_used=token,
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Update last access
        account.last_portal_access = timezone.now()
        account.save()
        
        # Generate statement
        statement = CustomerPortalService.generate_customer_statement(account)
        
        return render(request, 'accounts/customer_portal/customer_statement.html', {
            'account': account,
            'statement': statement,
            'business': account.khata.business
        })
        
    except Account.DoesNotExist:
        raise Http404("Invalid or expired access link")


@login_required
def share_customer_statement(request, account_id):
    """Generate shareable link for customer"""
    account = get_object_or_404(Account, id=account_id, khata__business=request.user.business)
    
    # Create shareable link
    shareable_url = CustomerPortalService.create_shareable_link(account)
    full_url = request.build_absolute_uri(shareable_url)
    
    # Here you would integrate with WhatsApp/SMS API
    # For now, just show success message
    messages.success(request, f'Shareable link created: {full_url}')
    
    return redirect('accounts:account_detail', pk=account_id)


# ============== SMART DASHBOARD FEATURES ===============

@login_required
def smart_dashboard(request):
    """Enhanced dashboard with business intelligence"""
    business = request.user.business
    
    # Today's summary
    today = timezone.now().date()
    today_entries = Roznamcha.objects.filter(
        khata__business=business,
        date=today
    )
    
    today_cash_in = today_entries.aggregate(total=Sum('cash_in'))['total'] or Decimal('0.00')
    today_cash_out = today_entries.aggregate(total=Sum('cash_out'))['total'] or Decimal('0.00')
    
    # Overdue customers
    overdue_customers = Account.objects.filter(
        khata__business=business,
        account_type='CUSTOMER',
        balance__gt=0,
        balance_type='DEBIT'
    )[:5]
    
    # Recent notifications
    recent_notifications = Notification.objects.filter(
        business=business
    ).order_by('-created_at')[:5]
    
    # Pending payments
    pending_payments = Payment.objects.filter(
        business=business,
        status='PENDING'
    ).count()
    
    context = {
        'today_cash_in': today_cash_in,
        'today_cash_out': today_cash_out,
        'net_cash_flow': today_cash_in - today_cash_out,
        'overdue_customers': overdue_customers,
        'recent_notifications': recent_notifications,
        'pending_payments': pending_payments,
        'total_customers': Account.objects.filter(
            khata__business=business, 
            account_type='CUSTOMER'
        ).count(),
        'total_suppliers': Account.objects.filter(
            khata__business=business, 
            account_type='SUPPLIER'
        ).count(),
    }
    
    return render(request, 'accounts/smart_dashboard.html', context)


# ============== API ENDPOINTS ===============

@csrf_exempt
def payment_webhook(request):
    """Handle payment gateway webhooks"""
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            transaction_id = payload.get('transaction_id')
            
            # Find payment
            payment = Payment.objects.get(transaction_id=transaction_id)
            
            # Update payment status
            payment.status = payload.get('status', 'COMPLETED')
            payment.gateway_response = payload
            payment.save()
            
            # Create roznamcha entry if completed
            if payment.status == 'COMPLETED':
                Roznamcha.objects.create(
                    khata=payment.account.khata,
                    account=payment.account,
                    date=timezone.now().date(),
                    cash_type='CASH_IN',
                    references=f"Payment: {payment.transaction_id}",
                    description=f"Payment received via {payment.payment_method.method_type}",
                    cash_in=payment.amount,
                    cash_out=0,
                    remaining=payment.account.balance
                )
                
                # Send payment received notification
                NotificationService.create_notification(
                    business=payment.business,
                    account=payment.account,
                    template_type='PAYMENT_RECEIVED',
                    scheduled_at=timezone.now(),
                    amount=payment.amount
                )
            
            return JsonResponse({'status': 'success'})
            
        except (Payment.DoesNotExist, json.JSONDecodeError) as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'method_not_allowed'})


@login_required
def dashboard_stats_api(request):
    """API endpoint for dashboard statistics"""
    business = request.user.business
    
    # Last 7 days cash flow
    cash_flow_data = []
    for i in range(7):
        date = timezone.now().date() - timedelta(days=i)
        entries = Roznamcha.objects.filter(khata__business=business, date=date)
        cash_in = entries.aggregate(total=Sum('cash_in'))['total'] or Decimal('0.00')
        cash_out = entries.aggregate(total=Sum('cash_out'))['total'] or Decimal('0.00')
        
        cash_flow_data.append({
            'date': date.isoformat(),
            'cash_in': float(cash_in),
            'cash_out': float(cash_out),
            'net': float(cash_in - cash_out)
        })
    
    return JsonResponse({
        'cash_flow_data': cash_flow_data
    })