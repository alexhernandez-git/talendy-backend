
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


def send_confirmation_email(user_pk):
    """Send account verification link to given user."""

    user = User.objects.get(pk=user_pk)
    verification_token = gen_verification_token(user)
    subject = 'Bienvenido @{}! Verifica tu cuenta para empezar a usar Classline Academy'.format(
        user.username)
    from_email = 'Classline Academy <no-reply@classlineacademy.com>'
    content = render_to_string(
        'emails/users/account_verification.html',
        {'token': verification_token, 'user': user}
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
    msg.attach_alternative(content, "text/html")
    msg.send()


def send_change_email(user, email):
    """Send account verification link to given user."""

    subject = 'Cambia el email de tu cuenta'.format(
        user.username)
    from_email = 'Classline Academy <no-reply@classlineacademy.com>'
    content = render_to_string(
        'emails/users/change_email.html',
        {'email': email, 'user': user}
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [email])
    msg.attach_alternative(content, "text/html")
    msg.send()


def send_reset_password(user, token):
    """Send account verification link to given user."""

    subject = 'Resetea la contraseña'
    from_email = 'Classline Academy <no-reply@classlineacademy.com>'
    content = render_to_string(
        'emails/users/reset_password.html',
        {'token': token, 'user': user}
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
    msg.attach_alternative(content, "text/html")
    msg.send()
