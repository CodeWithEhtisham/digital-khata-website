# Generated manually to properly handle business relationships
from django.db import migrations, models
import django.db.models.deletion


def assign_business_to_existing_records(apps, schema_editor):
    """Assign all existing Khata and Account records to the first business"""
    Business = apps.get_model('accounts', 'Business')
    Khata = apps.get_model('accounts', 'Khata')
    Account = apps.get_model('accounts', 'Account')
    
    # Get the first business (or create one if none exists)
    first_business = Business.objects.first()
    if not first_business:
        first_business = Business.objects.create(
            business_name="Default Business",
            business_email="admin@example.com",
            business_address="Default Address",
            business_contact="0000000000",
            business_owner="Admin",
            business_type="OTHER"
        )
    
    # Assign all existing khatas to the first business
    Khata.objects.update(business_id=first_business.id)
    
    # Assign all existing accounts to the first business
    Account.objects.update(business_id=first_business.id)


def reverse_assign_business(apps, schema_editor):
    """Reverse migration - no action needed"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_account_account_type_alter_account_balance_and_more'),
    ]

    operations = [
        # First, add the business field as nullable
        migrations.AddField(
            model_name='khata',
            name='business',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='khatas', to='accounts.business'),
        ),
        migrations.AddField(
            model_name='account',
            name='business',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='accounts.business'),
        ),
        
        # Run the data migration to assign existing records
        migrations.RunPython(assign_business_to_existing_records, reverse_assign_business),
        
        # Now make the field non-nullable
        migrations.AlterField(
            model_name='khata',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='khatas', to='accounts.business'),
        ),
        migrations.AlterField(
            model_name='account',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='accounts.business'),
        ),
        
        # Remove default from business_type field if it was added
        migrations.AlterField(
            model_name='business',
            name='business_type',
            field=models.CharField(choices=[('RETAIL', 'Retail Shop'), ('WHOLESALE', 'Wholesale'), ('SERVICE', 'Service Provider'), ('MANUFACTURING', 'Manufacturing'), ('TRADING', 'Trading Company'), ('OTHER', 'Other')], max_length=20),
        ),
        
        # Add unique constraints
        migrations.AlterUniqueTogether(
            name='khata',
            unique_together={('business', 'khata_name')},
        ),
        migrations.AlterUniqueTogether(
            name='account',
            unique_together={('business', 'name', 'khata')},
        ),
    ]