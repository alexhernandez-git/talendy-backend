
# Django
from api.plans.models.plans import Plan
import pdb
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.utils import timezone

# Models
from api.users.models import User
from api.activities.models import (
    Activity,
    CancelOrderActivity,
    ChangeDeliveryTimeActivity,
    DeliveryActivity,
    IncreaseAmountActivity,
    OfferActivity,
    RevisionActivity,
)

# Serializers
# Serializers
from api.activities.serializers import OfferActivityModelSerializer

# Utilities
import jwt
from datetime import timedelta
import geoip2.database
import ccy


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


def get_offer_token(user_token):
    """Create JWT token than the user change the email."""
    exp_date = timezone.now() + timedelta(days=3)
    payload = {
        'user_token': user_token,
        'exp': int(exp_date.timestamp()),
        'type': 'offer_token'
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
        Activity.DELIVERY: DeliveryActivity,
        Activity.REVISION: RevisionActivity,
        Activity.CANCEL: CancelOrderActivity,

    }
    activity_classes = switcher.get(type, None)
    model = None
    if "model" in activity_classes:
        model = activity_classes["model"]
    serializer = None
    if "serializer" in activity_classes:
        serializer = activity_classes["serializer"]
    return model, serializer
