"""Celery tasks."""

# Django
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

# Models
from api.users.models import User

# Celery
from celery.decorators import task

# Utilities
import jwt
import time
from datetime import timedelta
from api.utils import helpers
import re

@task(name='send_confirmation_email')
def send_confirmation_email(user_pk):
    """Send account verification link to given user."""

    user = User.objects.get(pk=user_pk)
    verification_token = helpers.gen_verification_token(user)
    subject = 'Welcome @{}! Verify your account to start using Full Order Tracker'.format(
        user.username)
    from_email = 'Full Order Tracker <no-reply@fullordertracker.com>'
    content = render_to_string(
        'emails/users/account_verification.html',
        {'token': verification_token, 'user': user}
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
    msg.attach_alternative(content, "text/html")
    msg.send()


@task(name='send_change_email_email')
def send_change_email_email(user_pk, new_email):
    """Send account verification link to given user."""

    user = User.objects.get(pk=user_pk)
    verification_token = helpers.gen_new_email_token(user, new_email)
    subject = 'Welcome @{}! Change your email'.format(
        user.username)
    from_email = 'Full Order Tracker <no-reply@fullordertracker.com>'
    content = render_to_string(
        'emails/users/change_email.html',
        {'token': verification_token, 'user': user}
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
    msg.attach_alternative(content, "text/html")
    msg.send()


@task(name='send_reset_password')
def send_reset_password_email(user_email):
    """Send account verification link to given user."""
    user = User.objects.get(email=user_email)
    verification_token = helpers.gen_verification_token(user)

    subject = 'Reset your password'
    from_email = 'Full Order Tracker <no-reply@fullordertracker.com>'
    content = render_to_string(
        'emails/users/reset_password.html',
        {'token': verification_token, 'user': user}
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
    msg.attach_alternative(content, "text/html")
    msg.send()
