
# Django

from api.users.models.karma_earnings import KarmaEarning
from api.plans.models.plans import Plan
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum

# DRF
from rest_framework import serializers

# Models
from api.donations.models import DonationOption
from api.users.models import User, Earning

from api.chats.models import Chat
from api.notifications.models import Notification, NotificationUser
from api.portals.models import Portal, PortalMember

# Serializers

# Utilities
import jwt
from datetime import timedelta
import geoip2.database
import ccy
import requests
import environ
import random
import string
env = environ.Env()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def gen_verification_token(user):

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


def get_random_username():
    r = None
    status = None
    try:
        r = requests.get('https://randomuser.me/api/?inc=login')
        status = r.status_code
    except:
        pass

    if status == 200:
        data = r.json()

        try:
            return data['results'][0]['login']['username']
        except:
            pass

    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))


def get_currency_api(current_login_ip):
    r = None
    status = None
    try:
        r = requests.get('http://ip-api.com/json/{}'.format(current_login_ip))
        status = r.status_code
    except:
        pass

    if status == 200:
        data = r.json()
        country_code = data['countryCode']
        if not country_code:
            country_code = "US"

        try:
            currency = ccy.countryccy(country_code)
            if DonationOption.objects.filter(currency=currency).exists():
                return currency
        except Exception as e:
            print(e)
            pass
        return "USD"
    else:
        raise serializers.ValidationError("Get currency issue, try it later")


def get_location_data(request):
    country_code = None
    currency = None
    country_name = None
    region = None
    region_name = None
    city = None
    zip = None
    lat = None
    lon = None
    current_login_ip = get_client_ip(request)
    # Remove this line in production
    if env.bool("DEBUG", default=True):
        current_login_ip = "147.161.106.227"
    # Get country
    r = None
    status = None
    try:
        r = requests.get('http://ip-api.com/json/{}'.format(current_login_ip))
        status = r.status_code
    except:
        pass

    if status == 200:
        data = r.json()
        country_code = data['countryCode']
        country_name = data['country']
        region = data['region']
        region_name = data['regionName']
        city = data['city']
        zip = data['zip']
        lat = data['lat']
        lon = data['lon']
        if not country_code:
            country_code = "US"

    # Get the currency by country
    if country_code:

        try:
            country_currency = ccy.countryccy(country_code)
            if DonationOption.objects.filter(currency=country_currency).exists():
                currency = country_currency
        except Exception as e:
            currency = "USD"
            print(e)
            pass
    else:
        currency = "USD"

    return currency, country_code, country_name, region, region_name, city, zip, lat, lon


def get_location_data_plan(request):
    country_code = None
    currency = None
    country_name = None
    region = None
    region_name = None
    city = None
    zip = None
    lat = None
    lon = None
    current_login_ip = get_client_ip(request)
    # Remove this line in production
    if env.bool("DEBUG", default=True):
        current_login_ip = "147.161.106.227"
    # Get country
    r = None
    status = None
    try:
        r = requests.get('http://ip-api.com/json/{}'.format(current_login_ip))
        status = r.status_code
    except:
        pass

    if status == 200:
        data = r.json()
        country_code = data['countryCode']
        country_name = data['country']
        region = data['region']
        region_name = data['regionName']
        city = data['city']
        zip = data['zip']
        lat = data['lat']
        lon = data['lon']
    if not country_code:
        country_code = "US"

    # Get the currency by country
    if country_code:

        try:
            country_currency = ccy.countryccy(country_code)
            if Plan.objects.filter(currency=country_currency).exists():
                currency = country_currency
        except Exception as e:
            currency = "USD"
            print(e)
            pass
    else:
        currency = "USD"

    return currency, country_code, country_name, region, region_name, city, zip, lat, lon


def get_currency_and_country_plan(user, request):

    country_code = user.country
    currency = user.currency
    if not currency:
        # Get country
        if not country_code:
            current_login_ip = get_client_ip(request)
            # Remove this line in production
            if env.bool("DEBUG", default=True):
                current_login_ip = "147.161.106.227"
            # Get country

            r = None
            status = None
            try:
                r = requests.get('http://ip-api.com/json/{}'.format(current_login_ip))
                status = r.status_code
            except:
                pass
            if status == 200:
                data = r.json()
                country_code = data['countryCode']
            if not country_code:
                country_code = "US"

        # Get the currency by country

        try:
            country_currency = ccy.countryccy(country_code)
            if Plan.objects.filter(currency=country_currency).exists():
                currency = country_currency
            else:
                currency = "USD"

        except Exception as e:
            print(e)
            currency = "USD"

            pass

    if not user.currency:
        user.currency = currency
    if not user.country:
        user.country = country_code
    user.save()
    return currency, country_code


def get_currency_and_country(request):
    user = request.user
    country_code = user.country
    currency = user.currency
    if not currency:
        # Get country
        if not user.country:
            current_login_ip = get_client_ip(request)
            # Remove this line in production
            if env.bool("DEBUG", default=True):
                current_login_ip = "147.161.106.227"
            # Get country

            r = None
            status = None
            try:
                r = requests.get('http://ip-api.com/json/{}'.format(current_login_ip))
                status = r.status_code
            except:
                pass
            if status == 200:
                data = r.json()
                country_code = data['countryCode']
                if not country_code:
                    country_code = "US"

            # Get the currency by country
            if country_code:

                try:
                    country_currency = ccy.countryccy(country_code)
                    if DonationOption.objects.filter(currency=country_currency).exists():
                        currency = country_currency
                except Exception as e:
                    print(e)
                    pass
            else:
                currency = "USD"
    if not user.currency:
        user.currency = currency
    if not user.country:
        user.country = country_code
    user.save()
    return currency, country_code


def get_plan(currency):
    plan = None

    try:
        plans_queryset = DonationOption.objects.filter(currency=currency)
        if plans_queryset.exists():
            plan = plans_queryset.first()

    except DonationOption.DoesNotExist:
        plans_queryset = DonationOption.objects.filter(currency="USD")
        if plans_queryset.exists():
            plan = plans_queryset.first()

    return plan


def get_portal_plan(currency, interval=Plan.MONTHLY):
    plan = None

    try:
        plans_queryset = Plan.objects.filter(currency=currency, interval=interval).order_by("unit_amount")
        if plans_queryset.exists():
            plan = plans_queryset.first()

    except Plan.DoesNotExist:
        plans_queryset = Plan.objects.filter(currency="USD", interval=Plan.MONTHLY).order_by("unit_amount")
        if plans_queryset.exists():
            plan = plans_queryset.first()

    return plan


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
    r = None
    status = None
    try:
        r = requests.get("https://api.exchangerate.host/"+rate_date+"?base=USD")
        status = r.status_code
    except:
        pass
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
    r = None
    status = None
    try:
        r = requests.get("https://api.exchangerate.host/"+rate_date+"?base="+base.upper())
        status = r.status_code
    except:
        pass

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


def addNewMemberToOficialPortal(user):
    # Add the user to oficial portal
    portal = get_object_or_404(Portal, url='oficial')

    member = PortalMember.objects.create(user=user, portal=portal, role=PortalMember.BASIC, is_active=True)
    portal.members_count += 1
    portal.active_members_count += 1
    portal.basic_members_count += 1
    portal.active_basic_members_count += 1
    portal.save()

    member.initial_karma_amount = 1000
    member.karma_amount += 1000
    member.karma_earned += 1000
    member.karma_earned_by_join_portal += 1000
    karma_earned = 1
    karma_spent = 1

    if member.karma_earned > 1:
        karma_earned = member.karma_earned
    if member.karma_spent > 1:
        karma_spent = member.karma_spent

    member.karma_ratio = karma_earned / karma_spent
    member.save()

    # Update user statistics
    KarmaEarning.objects.create(user=user, amount=1000, type=KarmaEarning.EARNED_BY_JOIN_PORTAL, portal=portal)

    user.portals_count += 1
    user.karma_amount += 1000
    user.karma_earned += 1000
    user.karma_earned_by_join_portal += 1000
    karma_earned = 1
    karma_spent = 1

    if user.karma_earned > 1:
        karma_earned = user.karma_earned
    if user.karma_spent > 1:
        karma_spent = user.karma_spent

    user.karma_ratio = karma_earned / karma_spent
    user.save()
