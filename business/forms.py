from django import forms
from accounts.models import Business, Khata

class BusinessForm(forms.ModelForm):
    """Form for creating and updating business details"""
    
    class Meta:
        model = Business
        fields = ['business_name', 'business_email', 'business_address', 'business_contact', 'business_owner']
        widgets = {
            'business_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter business name',
                'required': True
            }),
            'business_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter business email',
                'required': True
            }),
            'business_address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter business address',
                'rows': 3,
                'required': True
            }),
            'business_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact number',
                'pattern': r'[0-9+\-\s]+',
                'required': True
            }),
            'business_owner': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter owner name',
                'required': True
            }),
        }
        
    def clean_business_contact(self):
        contact = self.cleaned_data['business_contact']
        if not contact.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise forms.ValidationError("Please enter a valid contact number.")
        return contact


class KhataForm(forms.ModelForm):
    """Form for creating and managing Khata (business books)"""
    
    class Meta:
        model = Khata
        fields = ['khata_name']
        widgets = {
            'khata_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter khata name',
                'required': True
            }),
        }
        
    def clean_khata_name(self):
        name = self.cleaned_data['khata_name']
        if len(name.strip()) < 2:
            raise forms.ValidationError("Khata name must be at least 2 characters long.")
        return name.strip()