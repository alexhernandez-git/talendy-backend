# Generated by Django 3.0.3 on 2021-01-29 14:44

from django.db import migrations, models
import djmoney.models.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CancelOrder',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('reason', models.TextField(max_length=1000)),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ChangeDeliveryTime',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('reason', models.TextField(max_length=1000)),
                ('new_delivery_date', models.DateField()),
                ('new_order_time', models.IntegerField()),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('description', models.TextField(max_length=1000)),
                ('increase_amount', models.FloatField()),
                ('amount_increased', models.FloatField()),
                ('source_files', models.FileField(max_length=500, upload_to='orders/delivery/files/')),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Images',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(max_length=500, upload_to='orders/delivery/pictures/', verbose_name='Delivery image')),
            ],
        ),
        migrations.CreateModel(
            name='IncreaseAmount',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('reason', models.TextField(max_length=1000)),
                ('increase_amount', models.FloatField()),
                ('amount_increased', models.FloatField()),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('type', models.CharField(choices=[('NO', 'Two payments order'), ('TP', 'Two payments order'), ('RO', 'Recurrent order')], max_length=2)),
                ('interval_subscription', models.CharField(choices=[('AN', 'Annual'), ('MO', 'Month')], default='MO', max_length=2)),
                ('send_offer_by_email', models.BooleanField(default=False)),
                ('buyer_email', models.CharField(blank=True, max_length=150, null=True)),
                ('title', models.CharField(max_length=256)),
                ('description', models.TextField(max_length=1000)),
                ('total_amount_currency', djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('total_amount', djmoney.models.fields.MoneyField(decimal_places=2, default_currency='USD', max_digits=14)),
                ('first_payment_currency', djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('first_payment', djmoney.models.fields.MoneyField(blank=True, decimal_places=2, default_currency='USD', max_digits=14, null=True)),
                ('payment_at_delivery_currency', djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('payment_at_delivery', djmoney.models.fields.MoneyField(blank=True, decimal_places=2, default_currency='USD', max_digits=14, null=True)),
                ('delivery_date', models.DateTimeField(blank=True, null=True)),
                ('delivery_time', models.IntegerField(blank=True, null=True)),
                ('accepted', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('title', models.CharField(max_length=256)),
                ('description', models.TextField(max_length=1000)),
                ('total_amount_currency', djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('total_amount', djmoney.models.fields.MoneyField(decimal_places=2, default_currency='USD', max_digits=14)),
                ('first_payment_currency', djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('first_payment', djmoney.models.fields.MoneyField(blank=True, decimal_places=2, default_currency='USD', max_digits=14, null=True)),
                ('last_payment_currency', djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('last_payment', djmoney.models.fields.MoneyField(blank=True, decimal_places=2, default_currency='USD', max_digits=14, null=True)),
                ('delivery_date', models.DateTimeField()),
                ('order_time', models.IntegerField()),
                ('type', models.CharField(choices=[('NO', 'Two payments order'), ('TP', 'Two payments order'), ('RO', 'Recurrent order')], max_length=2)),
                ('interval_subscription', models.CharField(choices=[('AN', 'Annual'), ('MO', 'Month')], default='MO', max_length=2)),
                ('status', models.CharField(choices=[('AC', 'Active'), ('DE', 'Delivered'), ('CA', 'Cancelled')], default='AC', max_length=2)),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Revision',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('reason', models.TextField(max_length=2000)),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
    ]
