
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

    return token

def gen_new_email_token(user,new_email):
    """Create JWT token than the user change the email."""
    exp_date = timezone.now() + timedelta(days=3)
    payload = {
        'user': user.username,
        'email': new_email,
        'exp': int(exp_date.timestamp()),
        'type': 'change_email'
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    return token

# def send_confirmation_email(user_pk):
#     """Send account verification link to given user."""

#     user = User.objects.get(pk=user_pk)
#     verification_token = gen_verification_token(user)
#     subject = 'Welcome @{}! Verify your account to start using Full Order Tracker'.format(
#         user.username)
#     from_email = 'Full Order Tracker <no-reply@fullordertracker.com>'
#     content = render_to_string(
#         'emails/users/account_verification.html',
#         {'token': verification_token, 'user': user}
#     )
#     msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
#     msg.attach_alternative(content, "text/html")
#     msg.send()

