"""Users serializers."""

# Django REST Framework

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from django.contrib.gis.geos import Point

# Serializers
from api.users.serializers import UserModelSerializer
from api.posts.serializers import PostModelSerializer
from api.plans.serializers import PlanModelSerializer
from .plan_subscriptions import PlanSubscriptionModelSerializer

# Models
from api.portals.models import Portal, PlanSubscription, PortalMember
from api.users.models import User, UserLoginActivity, Earning, Connection, Follow, Blacklist, KarmaEarning
from api.plans.models import Plan


# Celery
from api.taskapp.tasks import (
    send_confirmation_email,
)

# Utils
from api.utils import helpers
import datetime
from django.utils import timezone
import tldextract


class PortalModelSerializer(serializers.ModelSerializer):
    """User model serializer."""
    plan = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Meta class."""

        model = Portal
        fields = (
            "id",
            "name",
            "url",
            "logo",
            "about",
            "donations_enabled",
            "users_count",
            "posts_count",
            "created_posts_count",
            "created_active_posts_count",
            "created_solved_posts_count",
            "collaborated_posts_count",
            "collaborated_active_posts_count",
            "collaborated_solved_posts_count",
            "free_trial_invoiced",
            "plan_default_payment_method",
            "have_active_plan",
            "is_free_trial",
            "passed_free_trial_once",
            "free_trial_expiration",
            "plan",
            "created"
        )

        read_only_fields = ("id",)

    def get_plan(self, obj):
        plan = PlanSubscription.objects.get(portal=obj, cancelled=False)
        return PlanSubscriptionModelSerializer(plan, many=False).data


class PortalListModelSerializer(serializers.ModelSerializer):
    """User model serializer."""
    owner = UserModelSerializer(read_only=True)
    members = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Meta class."""

        model = Portal
        fields = (
            "id",
            "name",
            "url",
            "about",
            "logo",
            "owner",
            "donations_enabled",
            "members"
        )

        read_only_fields = ("id",)

    def get_members(self, obj):

        return PortalMember.objects.filter(portal=obj.id).count()


class CreatePortalSerializer(serializers.Serializer):

    name = serializers.CharField(
        min_length=2,
        max_length=140,
        validators=[UniqueValidator(queryset=Portal.objects.all())],

    )

    url = serializers.SlugField(
        min_length=2,
        max_length=40,
        validators=[UniqueValidator(queryset=Portal.objects.all())],
    )

    about = serializers.CharField(allow_blank=True)

    logo = serializers.FileField(required=False, allow_null=True)

    # User login in case user is not authenticate
    email = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ],
        required=False,
        allow_blank=True
    )

    username = serializers.CharField(
        min_length=4,
        max_length=40,
        validators=[UniqueValidator(queryset=User.objects.all())],
        required=False,
        allow_blank=True

    )
    # Phone number
    phone_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: +999999999. Up to 15 digits allowed.",

    )
    phone_number = serializers.CharField(
        validators=[phone_regex], required=False, allow_blank=True)

    # Password
    password = serializers.CharField(min_length=8, max_length=64, required=False, allow_blank=True)
    password_confirmation = serializers.CharField(min_length=8, max_length=64, required=False, allow_blank=True)

    # Name
    first_name = serializers.CharField(min_length=2, max_length=30, required=False, allow_blank=True)
    last_name = serializers.CharField(min_length=2, max_length=30, required=False, allow_blank=True)

    # Currency for seller subscription
    currency = serializers.CharField(max_length=3, required=False, allow_blank=True)

    def validate(self, data):
        request = self.context['request']
        if not request.user.id:
            passwd = data['password']
            passwd_conf = data['password_confirmation']

            if passwd != passwd_conf:
                raise serializers.ValidationError('Password do not match')

        return data

    def create(self, validated_data):
        request = self.context['request']
        stripe = self.context['stripe']
        user = request.user

        # Check if user exists
        if not request.user.id:
            # Create the user
            currency, country, country_name, region, region_name, city, zip, lat, lon = helpers.get_location_data_plan(
                request)

            if not 'currency' in validated_data or not validated_data['currency'] and currency:
                validated_data['currency'] = currency

            karma_amount = 1000

            user = User.objects.create_user(
                email=validated_data['email'],
                username=validated_data['username'],
                password=validated_data['password'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                currency=validated_data['currency'],
                is_verified=False,
                is_client=True,
                country=country,
                country_name=country_name,
                region=region,
                region_name=region_name,
                city=city,
                zip=zip,
                geolocation=Point(lon, lat),
                karma_amount=karma_amount,
            )
            # Set the 1000 karma earned
            KarmaEarning.objects.create(user=user, amount=karma_amount, type=KarmaEarning.EARNED)
            user.karma_earned += karma_amount
            # Calc karma ratio
            karma_earned = 1
            karma_spent = 1

            if user.karma_earned > 1:
                karma_earned = user.karma_earned
            if user.karma_spent > 1:
                karma_spent = user.karma_spent
            user.karma_ratio = karma_earned / karma_spent
            user.save()
            token, created = Token.objects.get_or_create(
                user=user)

            current_login_ip = helpers.get_client_ip(request)

            if Blacklist.objects.filter(IP=current_login_ip).exists():
                raise serializers.ValidationError(
                    'Not allowed')

            if UserLoginActivity.objects.filter(user=user).exists():
                user_login_activity = UserLoginActivity.objects.filter(
                    user=user)[0]
                if user_login_activity.login_IP != current_login_ip:
                    if Token.objects.filter(user=user).exists():
                        last_token = Token.objects.get(user=user)
                        last_token.delete()
                UserLoginActivity.objects.filter(
                    login_username=user.username).delete()

            user_agent_info = request.META.get(
                'HTTP_USER_AGENT', '<unknown>')[:255],
            user_login_activity_log = UserLoginActivity(login_IP=helpers.get_client_ip(request),
                                                        user=user,
                                                        login_username=user.username,
                                                        user_agent_info=user_agent_info,
                                                        status=UserLoginActivity.SUCCESS)
            user_login_activity_log.save()

        # If the user is not a stripe customer, then create one

        if not user.stripe_customer_id:
            new_customer = stripe.Customer.create(
                description="talCustomer_"+user.first_name+'_'+user.last_name,
                name=user.first_name+' '+user.last_name,
                email=user.email,

            )
            user.stripe_customer_id = new_customer['id']
            user.save()

        # If user has no currency set then

        if user and not user.currency:
            currency, _ = helpers.get_currency_and_country_plan(
                user, request)
            user.currency = currency
            user.save()

        # Set default payment method the user default payment method

        if user.default_payment_method:
            stripe.Customer.modify(
                user.stripe_customer_id,
                invoice_settings={
                    "default_payment_method": user.default_payment_method
                }
            )

        # Get plan and start the free trial subscription

        plan = helpers.get_portal_plan(user.currency, Plan.MONTHLY)

        subscription = stripe.Subscription.create(
            customer=user.stripe_customer_id,
            items=[
                {"price": plan.stripe_price_id}
            ],
            trial_period_days="14",
        )

        # Create portal
        expiration_date = timezone.now() + datetime.timedelta(days=14)
        portal = Portal.objects.create(
            name=validated_data['name'],
            url=validated_data['url'],
            about=validated_data['about'],
            logo=validated_data.get('logo', None),
            owner=user,
            is_free_trial=True,
            free_trial_expiration=expiration_date,
            have_active_plan=True
        )

        # Add user to users in portal
        PortalMember.objects.create(portal=portal, user=user, role=PortalMember.ADMINISTRATOR)
        portal.users_count += 1
        portal.administrators_count += 1
        portal.save()

        user.portals_count += 1
        user.is_currency_permanent = True
        user.save()

        # Create plan subscription
        PlanSubscription.objects.create(
            user=user,
            portal=portal,
            subscription_id=subscription["id"],
            plan_unit_amount=plan.unit_amount,
            plan_currency=plan.currency,
            status=subscription['status'],
            plan_price_label=plan.price_label,
            plan_type=plan.type,
            product_id=plan.stripe_product_id,
            interval=plan.interval
        )

        if not request.user.id:
            send_confirmation_email(user)

        return {"portal": portal, "user": user, "access_token": str(Token.objects.get(user=user))}


class IsNameAvailableSerializer(serializers.Serializer):
    """Acount verification serializer."""

    name = serializers.CharField(allow_blank=True)

    def validate(self, data):
        """Update user's verified status."""

        name = data['name']

        if Portal.objects.filter(name=name).exists():
            raise serializers.ValidationError('This name is already in use')

        return {"name": name}


class IsUrlAvailableSerializer(serializers.Serializer):
    """Acount verification serializer."""

    url = serializers.CharField(allow_blank=True)

    def validate(self, data):
        """Update user's verified status."""

        url = data['url']

        if Portal.objects.filter(url=url).exists():
            raise serializers.ValidationError('This url is already in use')

        return {"url": url}


class AddBillingInformationSerializer(serializers.Serializer):
    """Acount verification serializer."""

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    payment_method_id = serializers.CharField(required=True)
    card_name = serializers.CharField(required=True)
    city = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    line1 = serializers.CharField(required=False, allow_blank=True)
    line2 = serializers.CharField(required=False, allow_blank=True)
    postal_code = serializers.CharField(required=True)
    state = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        """Update user's verified status."""
        stripe = self.context['stripe']
        request = self.context['request']
        portal = self.instance
        user = request.user
        payment_method_id = None

        if "payment_method_id" in data and data["payment_method_id"]:
            payment_method_id = data["payment_method_id"]
        else:
            raise serializers.ValidationError(
                'There is no payment method')

        currency, country = helpers.get_currency_and_country(request)
        subscriptions_queryset = PlanSubscription.objects.filter(user=user, portal=portal, cancelled=False)

        if subscriptions_queryset.exists():

            plan_subscription = subscriptions_queryset.first()
            plan_currency = plan_subscription.plan_currency
            interval = plan_subscription.interval
            if currency != plan_currency:
                plan = helpers.get_portal_plan(currency, interval)

                subscription = stripe.Subscription.retrieve(plan_subscription.subscription_id)

                stripe.Subscription.modify(
                    subscription["id"],
                    cancel_at_period_end=False,
                    proration_behavior=None,
                    items=[
                        {
                            'id': subscription['items']['data'][0].id,
                            "price": plan.stripe_price_id,
                        },
                    ]
                )
                plan_subscription.plan_type = plan.type
                plan_subscription.plan_currency = plan.currency
                plan_subscription.plan_unit_amount = plan.unit_amount
                plan_subscription.plan_price_label = plan.price_label
                plan_subscription.interval = plan.interval
                plan_subscription.save()

            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=user.stripe_customer_id,
            )
            stripe.Customer.modify(
                user.stripe_customer_id,
                address={
                    "city": data.get('city', " "),
                    "country": data.get('country', " "),
                    "line1": data.get('line1', " "),
                    "line2": data.get('line2', " "),
                    "postal_code": data.get('postal_code', " "),
                    "state": data.get('state', " "),
                },
                email=data.get('email', " "),
                name=data.get('first_name', " ")+"_"+data.get('last_name', " "),
                invoice_settings={
                    "default_payment_method": payment_method_id
                }
            )
            stripe.PaymentMethod.modify(
                payment_method_id,
                billing_details={
                    "name": data.get('card_name', " "),
                }
            )

        else:
            plan = helpers.get_portal_plan(user.currency)

            subscription = stripe.Subscription.create(
                customer=user.stripe_customer_id,
                items=[
                    {"price": plan.stripe_price_id}
                ],
            )
            plan_subscription = PlanSubscription.objects.create(
                user=user,
                subscription_id=subscription["id"],
                plan_unit_amount=plan.unit_amount,
                plan_currency=plan.currency,
                plan_price_label=plan.price_label,
                plan_type=plan.type,
                product_id=plan.stripe_product_id,
                interval=plan.interval
            )

        portal.have_active_plan = True
        portal.save()
        return data

    def update(self, instance, validated_data):
        request = self.context['request']
        user = request.user

        user.default_payment_method = validated_data['payment_method_id']
        instance.plan_default_payment_method = validated_data['payment_method_id']
        instance.save()

        return instance


class ChangePaymentMethodSerializer(serializers.Serializer):
    """Acount verification serializer."""

    payment_method_id = serializers.CharField(required=True)

    def validate(self, data):
        """Update user's verified status."""
        request = self.context['request']
        user = request.user
        portal = self.instance
        subscriptions_queryset = PlanSubscription.objects.filter(user=user, portal=portal, cancelled=False)

        if not subscriptions_queryset.exists():
            raise serializers.ValidationError(
                "Portal have not a plan subscription")

        return data

    def update(self, instance, validated_data):
        stripe = self.context['stripe']
        request = self.context['request']
        user = request.user
        portal = instance
        # Update subscription with new payment method

        # Get the subscription
        current_subscription = PlanSubscription.objects.filter(user=user, portal=portal, cancelled=False).first()

        stripe.Subscription.modify(
            current_subscription.subscription_id,
            default_payment_method=validated_data['payment_method_id']
        )
        instance.plan_default_payment_method = validated_data['payment_method_id']
        instance.save()
        return instance
