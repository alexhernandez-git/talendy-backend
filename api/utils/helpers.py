
# Django

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum

# DRF
from rest_framework import serializers

# Models
from api.plans.models import Plan
from api.users.models import User, Earning
from api.activities.models import (
    Activity,
    CancelOrderActivity,
    ChangeDeliveryTimeActivity,
    DeliveryActivity,
    IncreaseAmountActivity,
    OfferActivity,
    RevisionActivity,
)
from api.chats.models import Chat
from api.notifications.models import Notification, NotificationUser


# Serializers
from api.activities.serializers import (
    OfferActivityModelSerializer,
    DeliveryActivityModelSerializer,
    CancelOrderActivityModelSerializer,
    RevisionActivityModelSerializer
)

# Utilities
import jwt
from datetime import timedelta
import geoip2.database
import ccy
import requests
import datetime
import environ
env = environ.Env()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def gen_verification_token(user):
    """Create JWT token than the user can use to verify its account."""
    exp_date = timezone.now() + timedelta(days=3)
    payload = {
        'user': user.username,
        'exp': int(exp_date.timestamp()),
        'type': 'email_confirmation'
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    try:
        token = token.decode()
    except:
        pass
    return token


def gen_new_email_token(user, new_email):
    """Create JWT token than the user change the email."""
    exp_date = timezone.now() + timedelta(days=3)
    payload = {
        'user': user.username,
        'email': new_email,
        'exp': int(exp_date.timestamp()),
        'type': 'change_email'
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    try:
        token = token.decode()
    except:
        pass
    return token


def get_invitation_token(from_user, email):
    """Create JWT token than the user change the email."""
    exp_date = timezone.now() + timedelta(days=7)
    payload = {
        'from_user': str(from_user.pk),
        'to_user_email': email,
        'exp': int(exp_date.timestamp()),
        'type': 'invitation_token'
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    try:
        token = token.decode()
    except:
        pass
    return token


def get_user_token(user_id):
    """Create JWT token than the user can use to verify its account."""
    payload = {
        'user': str(user_id),
        'expiresIn': 0,
        'type': 'user_token'
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    try:
        token = token.decode()
    except:
        pass
    return token


def get_payment_methods(stripe, stripe_customer_id):
    if stripe_customer_id != None and stripe_customer_id != '':
        payment_methods = stripe.PaymentMethod.list(
            customer=stripe_customer_id,
            type="card"
        )
        return payment_methods.data
    else:
        return None


def get_currency_and_country_anonymous(request):
    country = None
    currency = None
    if not currency:
        # Get country
        if not country:
            current_login_ip = get_client_ip(request)
            # Remove this line in production
            if env.bool("DEBUG", default=True):
                current_login_ip = "37.133.187.101"
            # Get country
            try:
                with geoip2.database.Reader('geolite2-db/GeoLite2-Country.mmdb') as reader:
                    response = reader.country(current_login_ip)
                    country = response.country.iso_code
            except Exception as e:
                print(e)
                pass

            # Get the currency by country
            if country:

                try:
                    country_currency = ccy.countryccy(country)
                    if Plan.objects.filter(type=Plan.BASIC, currency=country_currency).exists():
                        currency = country_currency
                except Exception as e:
                    print(e)
                    pass
            else:
                currency = "USD"

    return currency, country


def get_currency_and_country(request):
    user = request.user
    country = user.country
    currency = user.currency
    if not currency:
        # Get country
        if not user.country:
            current_login_ip = get_client_ip(request)
            # Remove this line in production
            if env.bool("DEBUG", default=True):
                current_login_ip = "37.133.187.101"
            # Get country
            try:
                with geoip2.database.Reader('geolite2-db/GeoLite2-Country.mmdb') as reader:
                    response = reader.country(current_login_ip)
                    country = response.country.iso_code
            except Exception as e:
                print(e)
                pass

            # Get the currency by country
            if country:

                try:
                    country_currency = ccy.countryccy(country)
                    if Plan.objects.filter(type=Plan.BASIC, currency=country_currency).exists():
                        currency = country_currency
                except Exception as e:
                    print(e)
                    pass
            else:
                currency = "USD"
    if not user.currency:
        user.currency = currency
    if not user.country:
        user.country = country
    user.save()
    return currency, country


def get_plan(currency):
    plan = None

    try:
        plans_queryset = Plan.objects.filter(currency=currency, type=Plan.BASIC)
        if plans_queryset.exists():
            plan = plans_queryset.first()

    except Plan.DoesNotExist:
        plans_queryset = Plan.objects.filter(currency="USD", type=Plan.BASIC)
        if plans_queryset.exists():
            plan = plans_queryset.first()

    return plan


def get_activity_classes(type):
    switcher = {
        Activity.OFFER: {
            "model": OfferActivity,
            "serializer": OfferActivityModelSerializer
        },
        Activity.CHANGE_DELIVERY_TIME: ChangeDeliveryTimeActivity,
        Activity.INCREASE_AMOUNT: IncreaseAmountActivity,
        Activity.DELIVERY: {"model": DeliveryActivity, "serializer": DeliveryActivityModelSerializer},
        Activity.REVISION: {"model": RevisionActivity, "serializer": RevisionActivityModelSerializer},
        Activity.CANCEL: {
            "model": CancelOrderActivity,
            "serializer": CancelOrderActivityModelSerializer
        },

    }
    activity_classes = switcher.get(type, {"model": None, "serializer": None})
    model = None
    if "model" in activity_classes:
        model = activity_classes["model"]
    serializer = None
    if "serializer" in activity_classes:
        serializer = activity_classes["serializer"]
    return model, serializer


def get_chat(sent_by, sent_to):
    if not sent_by or not sent_to:
        return False

    chats = Chat.objects.filter(participants=sent_by)
    chats = chats.filter(participants=sent_to)
    if chats.exists():
        for chat in chats:
            if chat.participants.all().count() == 2:
                return chat
    return False


def get_currency_rate(currency, rate_date='latest'):
    r = requests.get("https://api.exchangeratesapi.io/"+rate_date+"?base=USD")
    status = r.status_code
    if status == 200:
        data = r.json()
        currency_rate = data['rates'][currency.upper()]
        currency_conversion_date = data['date']
        if not currency_rate:
            raise serializers.ValidationError("Currency rate not allowed")
    else:
        raise serializers.ValidationError("Rate conversion issue, try it later")
    return currency_rate, currency_conversion_date


def convert_currency(currency, base, price, rate_date='latest'):
    r = requests.get("https://api.exchangeratesapi.io/"+rate_date+"?base="+base.upper())
    status = r.status_code
    if status == 200:
        data = r.json()
        currency_rate = data['rates'][currency.upper()]
        currency_conversion_date = data['date']
        if not currency_rate:
            raise serializers.ValidationError("Currency rate not allowed")
        converted_currency = float(price) * currency_rate
    else:
        raise serializers.ValidationError("Rate conversion issue, try it later")
    return converted_currency, currency_conversion_date


def get_available_for_withdrawal(user):
    today = timezone.now()

    # Total earned
    earnings = Earning.objects.filter(
        user=user, type=Earning.ORDER_REVENUE, available_for_withdrawn_date__lt=today).aggregate(
        Sum('amount'))
    total_earned = earnings.get('amount__sum', None)

    # Total refunded
    refunded = Earning.objects.filter(
        user=user, type=Earning.REFUND, available_for_withdrawn_date__lt=today).aggregate(
        Sum('amount'))
    total_refunded = refunded.get('amount__sum', None)

    # Total spent
    spent = Earning.objects.filter(
        user=user, type=Earning.SPENT).aggregate(
        Sum('amount'))
    total_spent = spent.get('amount__sum', None)

    # Total withdrawn
    withdrawn = Earning.objects.filter(
        user=user, type=Earning.WITHDRAWN).aggregate(
        Sum('amount'))

    total_withdrawn = withdrawn.get('amount__sum', None)

    if not total_earned:
        total_earned = 0
    if not total_refunded:
        total_refunded = 0
    if not total_spent:
        total_spent = 0
    if not total_withdrawn:
        total_withdrawn = 0

    return total_earned + total_refunded - total_spent - total_withdrawn
