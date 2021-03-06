# Generated by Django 3.0.3 on 2021-05-19 10:21

from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DonationOption',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('type', models.CharField(choices=[('L1', 'Level 1'), ('L2', 'Level 2'), ('L3', 'Level 3'), ('L4', 'Level 4')], max_length=2)),
                ('unit_amount', models.FloatField(blank=True, null=True)),
                ('currency', models.CharField(blank=True, max_length=3, null=True)),
                ('price_label', models.CharField(blank=True, max_length=100, null=True)),
                ('stripe_price_id', models.CharField(blank=True, max_length=100, null=True)),
                ('stripe_product_id', models.CharField(blank=True, max_length=100, null=True)),
                ('paid_karma', models.FloatField()),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DonationPayment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('invoice_id', models.CharField(blank=True, max_length=100, null=True)),
                ('charge_id', models.CharField(blank=True, max_length=100, null=True)),
                ('amount_paid', models.FloatField()),
                ('currency', models.CharField(max_length=3)),
                ('paid', models.BooleanField(default=True)),
                ('status', models.CharField(blank=True, max_length=100, null=True)),
                ('invoice_pdf', models.CharField(blank=True, max_length=150, null=True)),
                ('stripe_price_id', models.CharField(blank=True, max_length=100, null=True)),
                ('stripe_product_id', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('is_other_amount', models.BooleanField(default=False)),
                ('is_anonymous', models.BooleanField(default=False)),
                ('email', models.CharField(blank=True, max_length=100, null=True)),
                ('message', models.TextField(blank=True, null=True)),
                ('gross_amount_currency', djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('gross_amount', djmoney.models.fields.MoneyField(decimal_places=2, default_currency='USD', max_digits=14)),
                ('net_amount_currency', djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('net_amount', djmoney.models.fields.MoneyField(decimal_places=2, default_currency='USD', max_digits=14)),
                ('service_fee_currency', djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('service_fee', djmoney.models.fields.MoneyField(decimal_places=2, default_currency='USD', max_digits=14)),
                ('rate_date', models.CharField(blank=True, max_length=20, null=True)),
                ('donation_option', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='donation_option_donation', to='donations.DonationOption')),
                ('donation_payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='donation_payment_donation', to='donations.DonationPayment')),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
    ]
