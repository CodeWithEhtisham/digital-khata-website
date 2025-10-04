from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import User, Account, Roznamcha, Business, Khata
from datetime import date

class CustomUserCreationForm(UserCreationForm):
    """Form for user registration - matching create_user.py functionality"""
    
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
            'required': True
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'required': True
        })
    )
    
    contact = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter contact number',
            'pattern': r'[0-9+\-\s]+',
            'required': True
        })
    )
    
    # Business fields
    business_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter business name',
            'required': True
        })
    )
    
    business_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter business email',
            'required': True
        })
    )
    
    business_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter business address',
            'rows': 3,
            'required': True
        })
    )
    
    business_contact = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter business contact',
            'pattern': r'[0-9+\-\s]+',
            'required': True
        })
    )
    
    business_type = forms.ChoiceField(
        choices=[
            ('', 'Select Business Type'),
            ('RETAIL', 'Retail Shop'),
            ('WHOLESALE', 'Wholesale'),
            ('SERVICE', 'Service Provider'),
            ('MANUFACTURING', 'Manufacturing'),
            ('TRADING', 'Trading Company'),
            ('OTHER', 'Other'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    # Payment integration fields
    enable_easypaisa = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input'
    }))
    easypaisa_account = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Easypaisa account number'
        })
    )
    
    enable_jazzcash = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input'
    }))
    jazzcash_account = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'JazzCash account number'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'name', 'email', 'contact', 'business_name', 'business_email', 'business_address', 'business_contact', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
        
    def save(self, commit=True):
        """Override save to create business and associate with user"""
        user = super().save(commit=False)
        user.name = self.cleaned_data['name']
        user.email = self.cleaned_data['email']
        user.contact = self.cleaned_data['contact']
        # Explicitly ensure these are False (should be default, but being explicit)
        user.is_staff = False
        user.is_superuser = False
        
        if commit:
            # First create the business
            business = Business.objects.create(
                business_name=self.cleaned_data['business_name'],
                business_email=self.cleaned_data['business_email'],
                business_address=self.cleaned_data['business_address'],
                business_contact=self.cleaned_data['business_contact'],
                business_owner=self.cleaned_data['name'],
                business_type=self.cleaned_data['business_type'],
                enable_easypaisa=self.cleaned_data['enable_easypaisa'],
                easypaisa_account=self.cleaned_data['easypaisa_account'],
                enable_jazzcash=self.cleaned_data['enable_jazzcash'],
                jazzcash_account=self.cleaned_data['jazzcash_account'],
            )
            
            # Associate user with the business
            user.business = business
            user.save()
            
            # Create a default khata for the business
            khata = Khata.objects.create(
                business=business,
                khata_name=f"{business.business_name} - Main Ledger"
            )
            
            # Initialize business services
            from .services import NotificationService, PaymentIntegrationService
            NotificationService.create_default_templates(business)
            PaymentIntegrationService.create_payment_methods(business)
            
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form - matching login_page.py functionality"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })


class UserUpdateForm(forms.ModelForm):
    """Form for updating user details - matching update_user_details.py"""
    
    class Meta:
        model = User
        fields = ['name', 'email', 'contact', 'username']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email'
            }),
            'contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact number'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter username'
            }),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form - matching update_password.py"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Current password'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'New password'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })


class AccountForm(forms.ModelForm):
    """Form for creating and updating accounts - matching add_accounts.py and update_accounts.py"""
    
    class Meta:
        model = Account
        fields = ['name', 'phone', 'address', 'balance_type', 'balance', 'khata']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter account name',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number',
                'pattern': r'[0-9+\-\s]+'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter address',
                'rows': 3
            }),
            'balance_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'khata': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        business = kwargs.pop('business', None)
        super().__init__(*args, **kwargs)
        
        # Filter khatas by business
        if business:
            self.fields['khata'].queryset = Khata.objects.filter(business=business)
        else:
            # If no business provided, show empty queryset
            self.fields['khata'].queryset = Khata.objects.none()
        
    def clean_balance(self):
        balance = self.cleaned_data.get('balance')
        # Convert empty values to 0 for database storage
        if balance is None or balance == '':
            return 0.00
        return balance


class RoznamchaForm(forms.ModelForm):
    """Form for creating and updating roznamcha entries - matching add_roznamcha.py and update_roznamcha.py"""
    
    class Meta:
        model = Roznamcha
        fields = ['khata', 'account', 'date', 'cash_type', 'references', 'description', 'cash_in', 'cash_out']
        widgets = {
            'khata': forms.Select(attrs={
                'class': 'form-control'
            }),
            'account': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'cash_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'references': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter reference'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter description',
                'rows': 3
            }),
            'cash_in': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'cash_out': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        business = kwargs.pop('business', None)
        super().__init__(*args, **kwargs)
        # Remove automatic date initialization to prevent preloaded values
        # Let user choose the date manually
        
        # Filter khatas and accounts by business
        if business:
            self.fields['khata'].queryset = Khata.objects.filter(business=business)
            self.fields['account'].queryset = Account.objects.filter(business=business)
        else:
            # If no business provided, show empty querysets
            self.fields['khata'].queryset = Khata.objects.none()
            self.fields['account'].queryset = Account.objects.none()
            
    def clean(self):
        cleaned_data = super().clean()
        cash_in = cleaned_data.get('cash_in') or 0
        cash_out = cleaned_data.get('cash_out') or 0
        
        # Ensure only one of cash_in or cash_out is filled
        if cash_in and cash_out:
            raise forms.ValidationError("Please enter either Cash In OR Cash Out, not both.")
        
        if not cash_in and not cash_out:
            raise forms.ValidationError("Please enter either Cash In or Cash Out amount.")
        
        # Convert empty values to 0 for database storage
        if not cash_in:
            cleaned_data['cash_in'] = 0
        if not cash_out:
            cleaned_data['cash_out'] = 0
            
        return cleaned_data
