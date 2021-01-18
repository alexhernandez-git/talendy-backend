
# Django
import pdb
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.utils import timezone

# Models
from api.users.models import User

# Utilities
import jwt
from datetime import timedelta


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


def get_payment_methods(stripe, stripe_customer_id):
    if stripe_customer_id != None and stripe_customer_id != '':
        payment_methods = stripe.PaymentMethod.list(
            customer=stripe_customer_id,
            type="card"
        )
        return payment_methods.data
    else:
        return None
