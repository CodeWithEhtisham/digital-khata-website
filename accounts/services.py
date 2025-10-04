"""
Smart Digital Khata Services
Handles notifications, payments, and business intelligence features
"""
from django.utils import timezone
from django.db.models import Q, Sum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import json
from typing import List, Dict, Any

from .models import (
    Business, Account, Roznamcha, Notification, NotificationTemplate,
    Payment, PaymentMethod, BusinessReport
)


class NotificationService:
    """Smart notification service for automated alerts and reminders"""
    
    @staticmethod
    def create_default_templates(business):
        """Create default notification templates for a new business"""
        default_templates = [
            {
                'template_type': 'PAYMENT_DUE',
                'channel': 'WHATSAPP',
                'subject': 'Payment Reminder',
                'message_template': 'السلام علیکم {name}! آپ کی باقی رقم {amount} PKR ہے۔ برائے کرم {due_date} تک ادائیگی کریں۔ شکریہ!\n\nHi {name}! Your outstanding amount is PKR {amount}. Please pay by {due_date}. Thank you!'
            },
            {
                'template_type': 'PAYMENT_OVERDUE',
                'channel': 'WHATSAPP',
                'subject': 'Payment Overdue',
                'message_template': '{name} صاحب، آپ کی {amount} PKR کی ادائیگی overdue ہے۔ فوری ادائیگی کریں۔\n\nDear {name}, your payment of PKR {amount} is overdue. Please pay immediately.'
            },
            {
                'template_type': 'PAYMENT_RECEIVED',
                'channel': 'WHATSAPP',
                'subject': 'Payment Received',
                'message_template': '{name} صاحب، آپ کی {amount} PKR کی ادائیگی موصول ہوئی۔ شکریہ!\n\nDear {name}, we received your payment of PKR {amount}. Thank you!'
            },
            {
                'template_type': 'ACCOUNT_STATEMENT',
                'channel': 'WHATSAPP',
                'subject': 'Account Statement',
                'message_template': '{name} صاحب، آپ کا کھاتہ statement attached ہے۔\n\nDear {name}, please find your account statement attached.'
            }
        ]
        
        for template_data in default_templates:
            NotificationTemplate.objects.get_or_create(
                business=business,
                template_type=template_data['template_type'],
                channel=template_data['channel'],
                defaults={
                    'subject': template_data['subject'],
                    'message_template': template_data['message_template']
                }
            )
    
    @staticmethod
    def schedule_payment_reminders(business):
        """Schedule payment due reminders for all overdue accounts"""
        today = timezone.now().date()
        
        # Find accounts with overdue payments
        overdue_accounts = Account.objects.filter(
            khata__business=business,
            balance__gt=0,
            balance_type='DEBIT'
        )
        
        for account in overdue_accounts:
            # Get last roznamcha entry to determine due date
            last_entry = account.roznamcha_entries.filter(cash_out__gt=0).first()
            if last_entry:
                due_date = last_entry.date + timedelta(days=account.payment_terms_days)
                
                if due_date <= today:
                    # Create overdue notification
                    NotificationService.create_notification(
                        business=business,
                        account=account,
                        template_type='PAYMENT_OVERDUE',
                        scheduled_at=timezone.now()
                    )
                elif due_date <= today + timedelta(days=3):
                    # Create due reminder
                    NotificationService.create_notification(
                        business=business,
                        account=account,
                        template_type='PAYMENT_DUE',
                        scheduled_at=timezone.now()
                    )
    
    @staticmethod
    def create_notification(business, account, template_type, scheduled_at, **kwargs):
        """Create a notification for an account"""
        try:
            # Get the appropriate template
            template = NotificationTemplate.objects.get(
                business=business,
                template_type=template_type,
                channel='WHATSAPP',  # Default to WhatsApp
                is_active=True
            )
            
            # Format the message
            message_data = {
                'name': account.name,
                'amount': str(account.balance),
                'due_date': kwargs.get('due_date', ''),
                **kwargs
            }
            
            formatted_message = template.message_template.format(**message_data)
            formatted_subject = template.subject
            if template.subject:
                formatted_subject = template.subject.format(**message_data)
            
            # Create notification
            notification = Notification.objects.create(
                business=business,
                account=account,
                template=template,
                recipient_phone=account.whatsapp_number or account.phone,
                recipient_email=account.email,
                subject=formatted_subject,
                message=formatted_message,
                scheduled_at=scheduled_at
            )
            
            return notification
            
        except NotificationTemplate.DoesNotExist:
            print(f"No template found for {template_type}")
            return None
    
    @staticmethod
    def send_pending_notifications():
        """Send all pending notifications (to be called by scheduler)"""
        pending_notifications = Notification.objects.filter(
            status='PENDING',
            scheduled_at__lte=timezone.now()
        )
        
        for notification in pending_notifications:
            # Here you would integrate with actual SMS/WhatsApp API
            # For now, we'll just mark as sent
            notification.status = 'SENT'
            notification.sent_at = timezone.now()
            notification.save()
            
            print(f"Sent notification to {notification.account.name}: {notification.message}")


class PaymentIntegrationService:
    """Handle payment gateway integrations"""
    
    @staticmethod
    def create_payment_methods(business):
        """Create default payment methods for business"""
        default_methods = [
            {
                'method_type': 'CASH',
                'account_number': 'CASH',
                'account_title': 'Cash Payments'
            }
        ]
        
        if business.enable_easypaisa and business.easypaisa_account:
            default_methods.append({
                'method_type': 'EASYPAISA',
                'account_number': business.easypaisa_account,
                'account_title': business.business_name
            })
            
        if business.enable_jazzcash and business.jazzcash_account:
            default_methods.append({
                'method_type': 'JAZZCASH',
                'account_number': business.jazzcash_account,
                'account_title': business.business_name
            })
            
        if business.enable_raast and business.raast_id:
            default_methods.append({
                'method_type': 'RAAST',
                'account_number': business.raast_id,
                'account_title': business.business_name
            })
        
        for method_data in default_methods:
            PaymentMethod.objects.get_or_create(
                business=business,
                method_type=method_data['method_type'],
                account_number=method_data['account_number'],
                defaults={
                    'account_title': method_data['account_title']
                }
            )
    
    @staticmethod
    def generate_raast_qr(business):
        """Generate RAAST QR code data"""
        if business.raast_id:
            qr_data = {
                'version': '01',
                'initiation_method': '11',
                'merchant_account': business.raast_id,
                'merchant_name': business.business_name,
                'merchant_city': 'Pakistan',
                'country_code': 'PK',
                'currency': 'PKR'
            }
            return json.dumps(qr_data)
        return None


class BusinessAnalyticsService:
    """Business intelligence and reporting service"""
    
    @staticmethod
    def generate_daily_summary(business, date=None):
        """Generate daily business summary"""
        if not date:
            date = timezone.now().date()
        
        # Get all roznamcha entries for the date
        entries = Roznamcha.objects.filter(
            khata__business=business,
            date=date
        )
        
        total_cash_in = entries.aggregate(total=Sum('cash_in'))['total'] or Decimal('0.00')
        total_cash_out = entries.aggregate(total=Sum('cash_out'))['total'] or Decimal('0.00')
        net_cash_flow = total_cash_in - total_cash_out
        
        # Customer payments received
        customer_payments = entries.filter(
            cash_in__gt=0,
            account__account_type='CUSTOMER'
        ).count()
        
        # Supplier payments made
        supplier_payments = entries.filter(
            cash_out__gt=0,
            account__account_type='SUPPLIER'
        ).count()
        
        summary_data = {
            'date': date.isoformat(),
            'total_cash_in': str(total_cash_in),
            'total_cash_out': str(total_cash_out),
            'net_cash_flow': str(net_cash_flow),
            'customer_payments_count': customer_payments,
            'supplier_payments_count': supplier_payments,
            'total_transactions': entries.count(),
        }
        
        # Save report
        report = BusinessReport.objects.create(
            business=business,
            report_type='DAILY_SUMMARY',
            start_date=date,
            end_date=date,
            report_data=summary_data
        )
        
        return report
    
    @staticmethod
    def get_customer_aging_report(business):
        """Generate customer aging report"""
        customers = Account.objects.filter(
            khata__business=business,
            account_type='CUSTOMER',
            balance__gt=0,
            balance_type='DEBIT'
        )
        
        aging_data = []
        for customer in customers:
            # Get oldest unpaid entry
            oldest_entry = customer.roznamcha_entries.filter(cash_out__gt=0).last()
            
            days_overdue = 0
            if oldest_entry:
                due_date = oldest_entry.date + timedelta(days=customer.payment_terms_days)
                days_overdue = (timezone.now().date() - due_date).days
            
            aging_category = 'Current'
            if days_overdue > 90:
                aging_category = '90+ Days'
            elif days_overdue > 60:
                aging_category = '60-90 Days'
            elif days_overdue > 30:
                aging_category = '30-60 Days'
            elif days_overdue > 0:
                aging_category = '1-30 Days'
            
            aging_data.append({
                'customer_name': customer.name,
                'balance': str(customer.balance),
                'days_overdue': days_overdue,
                'aging_category': aging_category,
                'phone': customer.phone,
                'last_payment_date': oldest_entry.date.isoformat() if oldest_entry else None
            })
        
        return aging_data


class CustomerPortalService:
    """Manage customer portal access and sharing"""
    
    @staticmethod
    def generate_customer_statement(account, start_date=None, end_date=None):
        """Generate customer account statement"""
        if not start_date:
            start_date = timezone.now().date() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now().date()
        
        entries = account.roznamcha_entries.filter(
            date__range=[start_date, end_date]
        ).order_by('date')
        
        statement_data = {
            'account_name': account.name,
            'statement_period': f"{start_date} to {end_date}",
            'opening_balance': str(account.balance),
            'entries': [],
            'closing_balance': str(account.balance)
        }
        
        running_balance = account.balance
        for entry in entries:
            running_balance = running_balance + entry.cash_in - entry.cash_out
            
            statement_data['entries'].append({
                'date': entry.date.isoformat(),
                'description': entry.description,
                'reference': entry.references,
                'cash_in': str(entry.cash_in),
                'cash_out': str(entry.cash_out),
                'balance': str(running_balance)
            })
        
        return statement_data
    
    @staticmethod
    def create_shareable_link(account):
        """Create secure shareable link for customer"""
        # Generate new token if needed
        if not account.portal_access_token:
            account.portal_access_token = uuid.uuid4()
            account.portal_access_enabled = True
            account.save()
        
        return f"/customer-portal/{account.portal_access_token}/"