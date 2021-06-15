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


class PortalModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = Portal
        fields = (
            "id",
            "name",
            "url",
            "donations_enabled"
        )

        read_only_fields = ("id",)


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
                description="claCustomer_"+user.first_name+'_'+user.last_name,
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
        portal = Portal.objects.create(
            name=validated_data['name'],
            url=validated_data['url'],
            about=validated_data['about'],
            logo=validated_data.get('logo', None),
            owner=user
        )

        # Add user to users in portal
        PortalMember.objects.create(portal=portal, user=user, role=PortalMember.ADMINISTRATOR)
        portal.all_users_count += 1
        portal.admins_count += 1
        portal.save()

        user.portals_count += 1
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

        send_confirmation_email(user)

        return {"user": user, "access_token": str(Token.objects.get(user=user))}
