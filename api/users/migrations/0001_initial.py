# Generated by Django 3.0.3 on 2021-04-13 07:48

from decimal import Decimal
from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import djmoney.models.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('notifications', '0001_initial'),
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('email', models.EmailField(blank=True, error_messages={'unique': 'Already exists a user with this email.'}, max_length=254, unique=True, verbose_name='email address')),
                ('username', models.CharField(max_length=150, unique=True)),
                ('about', models.TextField(blank=True, max_length=1000, null=True, verbose_name='about user')),
                ('picture', models.ImageField(blank=True, max_length=500, null=True, upload_to='users/pictures/', verbose_name='profile picture')),
                ('phone_number', models.CharField(blank=True, max_length=17, validators=[django.core.validators.RegexValidator(message='Phone number must be entered in the format: +999999999. Up to 15 digits allowed.', regex='\\+?1?\\d{9,15}$')])),
                ('is_client', models.BooleanField(default=True, help_text='Help easily distinguish users and perform queries. Clients are the main type of user.', verbose_name='client')),
                ('is_verified', models.BooleanField(default=False, help_text='Set to true when the user have verified its email address.', verbose_name='verified')),
                ('country', models.CharField(blank=True, max_length=2, null=True)),
                ('karmas_amount', models.IntegerField(default=1000)),
                ('stripe_customer_id', models.CharField(blank=True, max_length=100, null=True)),
                ('currency', models.CharField(blank=True, max_length=3, null=True)),
                ('default_payment_method', models.CharField(blank=True, max_length=100, null=True)),
                ('paypal_email', models.CharField(blank=True, max_length=100, null=True)),
                ('net_income_currency', djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('net_income', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0'), default_currency='USD', max_digits=14)),
                ('withdrawn_currency', djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('withdrawn', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0'), default_currency='USD', max_digits=14)),
                ('available_for_withdrawal_currency', djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('available_for_withdrawal', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0'), default_currency='USD', max_digits=14)),
                ('pending_clearance_currency', djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('pending_clearance', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0'), default_currency='USD', max_digits=14)),
                ('account_deactivated', models.BooleanField(default=False)),
                ('is_online', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='UserLoginActivity',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('login_IP', models.GenericIPAddressField(blank=True, null=True)),
                ('login_datetime', models.DateTimeField(auto_now=True)),
                ('login_username', models.CharField(blank=True, max_length=40, null=True)),
                ('status', models.CharField(blank=True, choices=[('S', 'Success'), ('F', 'Failed')], default='S', max_length=1, null=True)),
                ('user_agent_info', models.CharField(max_length=255)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user_login_activity',
                'verbose_name_plural': 'user_login_activities',
                'ordering': ['-login_datetime'],
            },
        ),
        migrations.CreateModel(
            name='RequestToConnect',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('form_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_user_request', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_user_request', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('follow_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_follow_user', to=settings.AUTH_USER_MODEL)),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_follow_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Earning',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('type', models.CharField(choices=[('DR', 'Donation Revenue'), ('WI', 'Withdrawn')], default='DR', max_length=2)),
                ('amount_currency', djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('amount', djmoney.models.fields.MoneyField(decimal_places=2, default_currency='USD', max_digits=14)),
                ('batch_id', models.CharField(blank=True, max_length=100, null=True)),
                ('available_for_withdrawn_date', models.DateTimeField(default=django.utils.timezone.now, help_text='Date time on pending clearance ends.', verbose_name='pending clearance expiration at')),
                ('setted_to_available_for_withdrawn', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('user_who_has_accepted', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_who_has_accepted', to=settings.AUTH_USER_MODEL)),
                ('user_who_has_requested', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_who_has_requested', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='user',
            name='followed',
            field=models.ManyToManyField(through='users.Follow', to=settings.AUTH_USER_MODEL, verbose_name='user_follow'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='notifications',
            field=models.ManyToManyField(related_name='user_notifications', through='notifications.NotificationUser', to='notifications.Notification'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
