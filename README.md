# 📊 Digital Khata - Multi-Tenant Business Accounting Platform

![Digital Khata](https://img.shields.io/badge/Digital_Khata-Business_Accounting-blue?style=for-the-badge)
![Django](https://img.shields.io/badge/Django-5.2.7-green?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.8+-yellow?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-red?style=for-the-badge)

Digital Khata is a modern, multi-tenant business accounting platform designed specifically for Pakistani businesses. It provides complete business isolation, smart notifications, payment integrations, and comprehensive financial management in a user-friendly interface.

## 🚀 Features

### 🏢 **Multi-Tenant Architecture**
- **Complete Business Isolation**: Each business sees only their own data
- **Scalable Design**: Support unlimited businesses on single platform
- **Secure Data Separation**: Zero cross-business data access
- **Role-Based Access Control**: Owner, Manager, Staff, Accountant roles

### 📈 **Core Accounting Features**
- **Digital Khata Management**: Create and manage multiple khatas per business
- **Account Management**: Customer, Supplier, Employee account tracking
- **Roznamcha (Ledger) System**: Complete transaction recording
- **Balance Tracking**: Real-time receivables and payables
- **Financial Overview**: Cash flow, profit/loss insights

### 🇵🇰 **Pakistan-Specific Features**
- **Currency Support**: PKR with proper formatting
- **CNIC Integration**: Customer identification support
- **Payment Methods**: Easypaisa, JazzCash, RAAST integration
- **Local Banking**: Bank transfer and cheque support
- **Urdu Language**: Bilingual interface (English/Urdu)

### 🔔 **Smart Notifications**
- **Automated Reminders**: Payment due alerts
- **Multi-Channel Support**: SMS, WhatsApp, Email
- **Custom Templates**: Personalized business messages
- **Overdue Alerts**: Automated follow-ups

### 💳 **Payment Integration**
- **Digital Wallets**: Easypaisa, JazzCash support
- **RAAST Integration**: Instant payment system
- **QR Code Generation**: Easy payment collection
- **Transaction Tracking**: Complete payment history

### 📊 **Business Analytics**
- **Financial Reports**: Daily, weekly, monthly summaries
- **Customer Aging**: Track overdue payments
- **Cash Flow Analysis**: Income vs expense tracking
- **Export Options**: PDF, Excel report generation

### 🌐 **Customer Portal**
- **Self-Service Access**: Customers view their statements
- **Secure Access Tokens**: UUID-based authentication
- **Payment History**: Complete transaction visibility
- **Mobile Responsive**: Works on all devices

## 🛠️ Technology Stack

- **Backend**: Django 5.2.7 (Python)
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Material Dashboard 3
- **Styling**: Bootstrap 5, Material Icons
- **Authentication**: Django Auth System
- **Forms**: Django Forms with validation

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git
- Virtual environment (recommended)

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/CodeWithEhtisham/digital-khata-website.git
cd digital-khata-website
```

### 2. Checkout Multi-Tenant Branch
```bash
git checkout feature/multi-tenant-architecture
```

### 3. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access Digital Khata.

## 📖 How to Use Digital Khata

### 🔐 **Getting Started**

#### 1. **Business Registration**
- Navigate to `/sign-up/`
- Fill in your personal information
- Enter your business details
- Configure payment methods (optional)
- Choose business type (Retail, Wholesale, Service, etc.)
- Create your account

#### 2. **First Login**
- Use your username and password to sign in
- You'll be redirected to your business dashboard
- A default khata is automatically created for your business

### 🏢 **Business Management**

#### **Dashboard Overview**
- **Statistics Cards**: Total businesses, khatas, accounts, net balance
- **Cash Flow Summary**: Visual representation of income/expenses
- **Quick Actions**: Fast access to create accounts and entries
- **Recent Activities**: Latest accounts and transactions
- **Account Statistics**: Balance distribution charts

#### **Managing Khatas**
A Khata is like a separate accounting book for different aspects of your business.

```
Examples:
- Main Khata: General business transactions
- Shop Khata: Retail operations
- Wholesale Khata: Bulk sales
- Services Khata: Service-based income
```

### 👥 **Account Management**

#### **Creating Accounts**
1. Go to **Accounts** → **Create Account**
2. Fill in account details:
   - **Account Name**: Customer/Supplier name
   - **Phone Number**: Contact information
   - **Select Khata**: Choose appropriate khata
   - **Account Type**: 
     - **Receivable**: Customer owes you money
     - **Payable**: You owe them money
   - **Opening Balance**: Initial balance (optional)
   - **Address**: Contact address (optional)

#### **Account Types**
- **Customer**: People who buy from you
- **Supplier**: People you buy from
- **Employee**: Staff members
- **Other**: Any other business contacts

### 📝 **Roznamcha (Transaction Recording)**

#### **Adding Entries**
1. Go to **Roznamcha** → **Create Entry**
2. Fill in transaction details:
   - **Select Khata**: Choose the khata
   - **Select Account**: Choose customer/supplier
   - **Date**: Transaction date
   - **Cash Type**: Cash In or Cash Out
   - **Reference**: Invoice/receipt number
   - **Description**: Transaction details
   - **Amount**: Enter in Cash In OR Cash Out (not both)

#### **Understanding Cash Flow**
- **Cash In**: Money received (sales, payments from customers)
- **Cash Out**: Money paid (purchases, payments to suppliers)

### 💰 **Payment Integration**

#### **Setting Up Payment Methods**
1. During registration, enable:
   - **Easypaisa**: Enter your Easypaisa account number
   - **JazzCash**: Enter your JazzCash account number
2. Configure during business operation:
   - **RAAST**: Add your RAAST ID
   - **Bank Account**: Add bank details

#### **Processing Payments**
- Generate QR codes for easy payment collection
- Track payment status (Pending, Processing, Completed)
- Link payments to specific roznamcha entries

### 📊 **Reports and Analytics**

#### **Available Reports**
- **Daily Summary**: Today's transactions
- **Weekly Summary**: Week's performance
- **Monthly Summary**: Month's financial overview
- **Profit & Loss**: Income vs expenses
- **Cash Flow**: Money in vs money out
- **Customer Aging**: Overdue payment tracking

#### **Exporting Reports**
- Download as PDF for printing
- Export to Excel for further analysis
- Share via email or WhatsApp

### 🔔 **Smart Notifications**

#### **Automated Alerts**
- **Payment Due**: 3 days before due date
- **Payment Overdue**: Daily reminders after due date
- **Payment Received**: Confirmation messages
- **Account Statements**: Weekly/monthly summaries

#### **Notification Channels**
- **SMS**: Text message alerts
- **WhatsApp**: WhatsApp Business messages
- **Email**: Email notifications

### 🌐 **Customer Portal**

#### **Enabling Customer Access**
1. Go to account details
2. Enable "Portal Access"
3. Share the access token with customer
4. Customer can view their statement anytime

#### **Customer Benefits**
- View transaction history
- Check current balance
- Download statements
- Make payment requests

## 🏗️ Advanced Configuration

### 🐳 **Production Deployment**

#### **Environment Variables**
Create a `.env` file:
```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_URL=postgres://user:pass@localhost:5432/digitalkhata
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

#### **Database Configuration**
For PostgreSQL:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'digitalkhata',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 📱 **SMS/WhatsApp Integration**

#### **Configure SMS Gateway**
```python
# Add to settings.py
SMS_API_KEY = 'your-sms-api-key'
SMS_SENDER_ID = 'DKHATA'
```

#### **WhatsApp Business API**
```python
WHATSAPP_TOKEN = 'your-whatsapp-business-token'
WHATSAPP_PHONE_ID = 'your-phone-number-id'
```

### 💳 **Payment Gateway Setup**

#### **Easypaisa Integration**
```python
EASYPAISA_MERCHANT_ID = 'your-merchant-id'
EASYPAISA_API_KEY = 'your-api-key'
```

#### **JazzCash Integration**
```python
JAZZCASH_MERCHANT_ID = 'your-merchant-id'
JAZZCASH_PASSWORD = 'your-password'
JAZZCASH_INTEGRITY_SALT = 'your-integrity-salt'
```

## 🔧 Customization

### 🎨 **Theming**
- Modify `static/css/custom.css` for custom styling
- Update Material Dashboard colors in `static/css/material-dashboard.css`
- Add your logo in `static/img/logo.png`

### 🌐 **Localization**
- Add Urdu translations in `locale/ur/LC_MESSAGES/`
- Configure language settings in `settings.py`
- Use Django's translation framework

### 📊 **Custom Reports**
- Create new report types in `models.py`
- Add report generation in `services.py`
- Include templates in `templates/reports/`

## 🚀 Production Best Practices

### 🔒 **Security**
- Use HTTPS in production
- Set strong SECRET_KEY
- Configure proper ALLOWED_HOSTS
- Enable CSRF protection
- Use environment variables for sensitive data

### ⚡ **Performance**
- Use PostgreSQL for production
- Configure Redis for caching
- Enable compression middleware
- Optimize static file serving

### 🔍 **Monitoring**
- Set up logging for errors
- Monitor database performance
- Track user activity
- Set up backup systems

## 🤝 Contributing

We welcome contributions to Digital Khata!

### **How to Contribute**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### **Development Setup**
1. Follow the Quick Start guide
2. Install development dependencies: `pip install -r requirements-dev.txt`
3. Run tests: `python manage.py test`
4. Follow PEP 8 coding standards

## 🐛 Troubleshooting

### **Common Issues**

#### **Empty Khata Dropdown**
- **Problem**: No khatas appear in account creation
- **Solution**: Ensure your user is assigned to a business and the business has khatas

#### **Form Validation Errors**
- **Problem**: Red borders on form fields
- **Solution**: Check required fields and ensure proper data formats

#### **Permission Denied**
- **Problem**: Users can't access certain features
- **Solution**: Check user role and business assignment

#### **Payment Integration Issues**
- **Problem**: Payments not processing
- **Solution**: Verify API keys and account credentials

### **Getting Help**
- Check the [Issues](https://github.com/CodeWithEhtisham/digital-khata-website/issues) page
- Create a new issue for bugs
- Contact support for business inquiries

## 📞 Support

- **Email**: support@digitalkhata.com
- **GitHub Issues**: [Create an Issue](https://github.com/CodeWithEhtisham/digital-khata-website/issues)
- **Documentation**: [Wiki](https://github.com/CodeWithEhtisham/digital-khata-website/wiki)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Django Framework**: For the robust web framework
- **Material Dashboard**: For the beautiful UI components
- **Pakistani Business Community**: For inspiration and feedback
- **Contributors**: All developers who helped build this platform

## 🎯 Future Roadmap

- [ ] Mobile app development (iOS/Android)
- [ ] Advanced inventory management
- [ ] Multi-currency support
- [ ] AI-powered insights
- [ ] Blockchain transaction verification
- [ ] Advanced reporting dashboard
- [ ] Integration with popular accounting software
- [ ] Voice-activated transaction recording

---

**Made with ❤️ for Pakistani Businesses**

*Digital Khata - Simplifying Business Accounting, One Transaction at a Time*
