# Generated by Django 3.0.3 on 2021-01-27 13:20

from django.db import migrations, models
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20210126_2054'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offer',
            name='amount_at_delivery',
        ),
        migrations.RemoveField(
            model_name='order',
            name='amount_at_delivery',
        ),
        migrations.RemoveField(
            model_name='order',
            name='is_split_payment',
        ),
        migrations.AddField(
            model_name='offer',
            name='interval_subscription',
            field=models.CharField(choices=[('AN', 'Annual'), ('MO', 'Month')], default='MO', max_length=2),
        ),
        migrations.AddField(
            model_name='offer',
            name='last_payment',
            field=djmoney.models.fields.MoneyField(blank=True, decimal_places=2, default_currency='USD', max_digits=14, null=True),
        ),
        migrations.AddField(
            model_name='offer',
            name='last_payment_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3),
        ),
        migrations.AddField(
            model_name='order',
            name='first_payment_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3),
        ),
        migrations.AddField(
            model_name='order',
            name='interval_subscription',
            field=models.CharField(choices=[('AN', 'Annual'), ('MO', 'Month')], default='MO', max_length=2),
        ),
        migrations.AddField(
            model_name='order',
            name='last_payment',
            field=djmoney.models.fields.MoneyField(blank=True, decimal_places=2, default_currency='USD', max_digits=14, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='last_payment_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3),
        ),
        migrations.AddField(
            model_name='order',
            name='total_amount_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='offer',
            name='days_for_delivery',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='offer',
            name='delivery_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='order',
            name='first_payment',
            field=djmoney.models.fields.MoneyField(blank=True, decimal_places=2, default_currency='USD', max_digits=14, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_amount',
            field=djmoney.models.fields.MoneyField(decimal_places=2, default_currency='USD', max_digits=14),
        ),
    ]
