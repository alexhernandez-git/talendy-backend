"""Celery tasks."""

# Django
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.module_loading import import_string

# Models
from api.users.models import User

# Celery
from celery.decorators import task

# Utilities
import jwt
import time
from django.utils import timezone
from api.utils import helpers
import re


@task(name='send_confirmation_email', max_retries=3)
def send_confirmation_email(user):
    """Send account verification link to given user."""

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


@task(name='send_change_email_email', max_retries=3)
def send_change_email_email(user, new_email):
    """Send account verification link to given user."""

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


@task(name='send_reset_password', max_retries=3)
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


@task(name='send_invitation_email', max_retries=3)
def send_invitation_email(user, email, message, type):
    """Send account verification link to given user."""

    verification_token = helpers.get_invitation_token(user, email)
    subject = 'Welcome! @{} has invited you '.format(
        user.username)
    from_email = 'Full Order Tracker <no-reply@fullordertracker.com>'
    content = render_to_string(
        'emails/users/user_invitation.html',
        {'token': verification_token, 'user': user, 'message': message, 'type': type}
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [email])
    msg.attach_alternative(content, "text/html")
    msg.send()


@task(name='send_offer', max_retries=3)
def send_offer(user, email, invitation):
    """Send account verification link to given user."""

    verification_token = helpers.get_invitation_offer_token(user, email)
    subject = 'Welcome! @{} has invited you '.format(
        user.username)
    from_email = 'Full Order Tracker <no-reply@fullordertracker.com>'
    content = render_to_string(
        'emails/users/order_offer.html',
        {'token': verification_token, 'user': user, 'invitation': invitation}
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [email])
    msg.attach_alternative(content, "text/html")
    msg.send()


@task(name='check_if_free_trial_have_ended')
def check_if_free_trial_have_ended():
    """Check if the free trial has ended and turn off"""
    now = timezone.now()

    # Update rides that have already finished
    users = User.objects.filter(
        free_trial_expiration__gte=now,
        is_free_trial=True
    )
    users.update(is_free_trial=False, passed_free_trial_once=True)
    print("Users that has been updated")
    print("Total: "+str(users.count()))
    for user in users:
        print("---------------------------------")
        print(user.username)


@task
def update_rates(backend=settings.EXCHANGE_BACKEND, **kwargs):
    backend = import_string(backend)()
    backend.update_rates(**kwargs)
