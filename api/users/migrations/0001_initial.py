# Generated by Django 3.0.3 on 2021-03-28 13:36

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
                ('is_seller', models.BooleanField(default=False, help_text='Set to true when the user have a seller account.', verbose_name='seller')),
                ('seller_view', models.BooleanField(default=False, help_text='Set to true when the user view is on seller dashboard set false if is in buyer view.', verbose_name='seller view')),
                ('is_free_trial', models.BooleanField(default=False, help_text='Set to true when the seller is in free trial.', verbose_name='free trial')),
                ('passed_free_trial_once', models.BooleanField(default=False, help_text='Set to true when the seller alreay passed free trial once.', verbose_name='passed free trial')),
                ('free_trial_expiration', models.DateTimeField(blank=True, help_text='Date time on the free tiral expiration.', null=True, verbose_name='free trial expiration at')),
                ('have_active_plan', models.BooleanField(default=False, help_text='Set to true when the user have a active plan subscription.', verbose_name='have active plan subscription')),
                ('stripe_plan_customer_id', models.CharField(blank=True, max_length=100, null=True)),
                ('plan_default_payment_method', models.CharField(blank=True, max_length=100, null=True)),
                ('active_month', models.BooleanField(default=False)),
                ('stripe_customer_id', models.CharField(blank=True, max_length=100, null=True)),
                ('currency', models.CharField(blank=True, max_length=3, null=True)),
                ('default_payment_method', models.CharField(blank=True, max_length=100, null=True)),
                ('paypal_email', models.CharField(blank=True, max_length=100, null=True)),
                ('net_income_currency', djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('net_income', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0'), default_currency='USD', max_digits=14)),
                ('withdrawn_currency', djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('withdrawn', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0'), default_currency='USD', max_digits=14)),
                ('used_for_purchases_currency', djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('used_for_purchases', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0'), default_currency='USD', max_digits=14)),
                ('available_for_withdrawal_currency', djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('available_for_withdrawal', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0'), default_currency='USD', max_digits=14)),
                ('pending_clearance_currency', djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('pending_clearance', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0'), default_currency='USD', max_digits=14)),
                ('messages_notificatoin_sent', models.BooleanField(default=False)),
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
            name='PlanSubscription',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('subscription_id', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.CharField(blank=True, max_length=100, null=True)),
                ('product_id', models.CharField(blank=True, max_length=100, null=True)),
                ('to_be_cancelled', models.BooleanField(default=False)),
                ('cancelled', models.BooleanField(default=False)),
                ('payment_issue', models.BooleanField(default=False)),
                ('current_period_end', models.IntegerField(blank=True, default=0)),
                ('plan_type', models.CharField(choices=[('BA', 'Basic')], max_length=2)),
                ('plan_unit_amount', models.FloatField(blank=True, null=True)),
                ('plan_currency', models.CharField(blank=True, max_length=3, null=True)),
                ('plan_price_label', models.CharField(blank=True, max_length=100, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PlanPayment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('invoice_id', models.CharField(blank=True, max_length=100, null=True)),
                ('charge_id', models.CharField(blank=True, max_length=100, null=True)),
                ('subscription_id', models.CharField(blank=True, max_length=100, null=True)),
                ('amount_paid', models.FloatField()),
                ('currency', models.CharField(max_length=3)),
                ('paid', models.BooleanField(default=True)),
                ('status', models.CharField(blank=True, max_length=100, null=True)),
                ('invoice_pdf', models.CharField(blank=True, max_length=150, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_payments', to=settings.AUTH_USER_MODEL)),
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
                ('type', models.CharField(choices=[('OR', 'Order revenue'), ('WI', 'Withdrawn'), ('RE', 'Refund'), ('SP', 'Spent')], default='OR', max_length=2)),
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
            name='Contact',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('contact_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_contact_user', to=settings.AUTH_USER_MODEL)),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_contact_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='user',
            name='contacts',
            field=models.ManyToManyField(through='users.Contact', to=settings.AUTH_USER_MODEL, verbose_name='user_contacts'),
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
