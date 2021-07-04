"""Celery tasks."""

# Django
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.module_loading import import_string
from django.core import management

# Models
from api.users.models import User, Earning
from rest_framework.authtoken.models import Token
from api.notifications.models import NotificationUser, notifications
from djmoney.money import Money

# Celery
from celery.decorators import task

# Utilities
import jwt
import time
from django.utils import timezone
from api.utils import helpers
import re


@task(name='send_feedback_email', max_retries=3)
def send_feedback_email(data):
    """Send account verification link to given user."""

    subject = 'Feedback from'.format(
        data['email'])
    from_email = 'Talendy <no-reply@talendy.com>'
    content = render_to_string(
        'emails/users/feedback_email.html',
        {'data': data}
    )
    msg = EmailMultiAlternatives(subject, content, from_email, ["ah30456@gmail.com"])
    msg.attach_alternative(content, "text/html")
    msg.send()


@task(name='send_confirmation_email', max_retries=3)
def send_confirmation_email(user):
    """Send account verification link to given user."""

    verification_token = helpers.gen_verification_token(user)
    subject = 'Welcome @{}! Verify your account to start using Talendy'.format(
        user.username)
    from_email = 'Talendy <no-reply@talendy.com>'
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
    from_email = 'Talendy <no-reply@talendy.com>'
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
    from_email = 'Talendy <no-reply@talendy.com>'
    content = render_to_string(
        'emails/users/reset_password.html',
        {'token': verification_token, 'user': user}
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
    msg.attach_alternative(content, "text/html")
    msg.send()


@task(name='send_invitation_email', max_retries=3)
def send_invitation_email(user, to_user):
    """Send account verification link to given user."""

    subject = 'Welcome! @{} has invited you '.format(
        user.username)
    from_email = 'Talendy <no-reply@talendy.com>'
    content = render_to_string(
        'emails/users/connect_invitation.html',
        {'user': user}

    )
    msg = EmailMultiAlternatives(subject, content, from_email, [to_user.email])
    msg.attach_alternative(content, "text/html")
    msg.send()


@task(name='send_post_to_followers', max_retries=3)
def send_post_to_followers(user, to_user, post):
    """Send account verification link to given user."""

    subject = '@{} has just created new post'.format(
        user.username)
    from_email = 'Talendy <no-reply@talendy.com>'

    content = render_to_string(
        'emails/users/new_post.html',
        {'user': user, 'post': post}
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [to_user.email])
    msg.attach_alternative(content, "text/html")
    msg.send()


@task(name='send_have_messages_from_email', max_retries=3)
def send_have_messages_from_email(sent_to, sent_by):
    """Check if the free trial has ended and turn off"""

    subject = 'New messages from @{}'.format(
        sent_by.username)

    from_email = 'Talendy <no-reply@talendy.com>'
    content = render_to_string(
        'emails/users/new_messages.html',
        {'user': sent_by}
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [sent_to.email])
    msg.attach_alternative(content, "text/html")
    msg.send()


@task(name='send_have_collaborate_room_messages_from_email', max_retries=3)
def send_have_collaborate_room_messages_from_email(sent_to, sent_by, post):
    """Check if the free trial has ended and turn off"""

    subject = 'New collaborate room messages from @{}'.format(
        sent_by.username)

    from_email = 'Talendy <no-reply@talendy.com>'
    content = render_to_string(
        'emails/users/new_room_messages.html',
        {'user': sent_by, 'post': post}
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [sent_to.email])
    msg.attach_alternative(content, "text/html")
    msg.send()


@task(name='send_connection_accepted', max_retries=3)
def send_connection_accepted(user, sent_to):
    """Check if the free trial has ended and turn off"""

    subject = '@{} is your new connection'.format(
        user.username)

    from_email = 'Talendy <no-reply@talendy.com>'
    content = render_to_string(
        'emails/users/connection_accepted.html',
        {'user': user}
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [sent_to.email])
    msg.attach_alternative(content, "text/html")
    msg.send()


@task(name='send_collaborate_request', max_retries=3)
def send_collaborate_request(user, sent_to):
    """Check if the free trial has ended and turn off"""

    subject = 'New collaborate request from @{}'.format(
        user.username)

    from_email = 'Talendy <no-reply@talendy.com>'
    content = render_to_string(
        'emails/users/collaborate_request.html',
        {'user': user}
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [sent_to.email])
    msg.attach_alternative(content, "text/html")
    msg.send()


@task(name='send_collaborate_request_accepted', max_retries=3)
def send_collaborate_request_accepted(post, sent_to):
    """Check if the free trial has ended and turn off"""

    subject = 'Collaborate request accepted by @{}'.format(
        post.user.username)

    from_email = 'Talendy <no-reply@talendy.com>'
    content = render_to_string(
        'emails/users/collaborate_request_accepted.html',
        {'post': post}
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [sent_to.email])
    msg.attach_alternative(content, "text/html")
    msg.send()


@task(name='send_post_finalized', max_retries=3)
def send_post_finalized(user, sent_to, post):
    """Check if the free trial has ended and turn off"""

    subject = '@{} has finalized the post'.format(
        user.username)

    from_email = 'Talendy <no-reply@talendy.com>'
    content = render_to_string(
        'emails/users/post_finalized.html',
        {'user': user, 'post': post}
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [sent_to.email])
    msg.attach_alternative(content, "text/html")
    msg.send()


@task(name='send_new_donation', max_retries=3)
def send_new_donation(user, sent_to, is_anonymous):
    """Check if the free trial has ended and turn off"""

    if is_anonymous:
        subject = 'You recieved new donation from anonymous user'
    else:
        subject = 'You recieved new donation from @{}'.format(
            user.username)
    from_email = 'Talendy <no-reply@talendy.com>'
    content = render_to_string(
        'emails/users/new_donation.html',
        {'user': user, 'is_anonymous': is_anonymous}
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [sent_to.email])
    msg.attach_alternative(content, "text/html")
    msg.send()


@task(name='send_portal_access', max_retries=3)
def send_portal_access(member, portal):
    """Check if the free trial has ended and turn off"""

    subject = '@{} access to portal of the'.format(
        portal.name)

    from_email = 'Talendy <no-reply@talendy.com>'
    content = render_to_string(
        'emails/users/access_to_portal.html',
        {'member': member, 'portal': portal}
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [member.email])
    msg.attach_alternative(content, "text/html")
    msg.send()

# MESSAGES = 'ME'
# NEW_INVITATION = 'NI'
# NEW_CONNECTION = 'NC'
# NEW_COLLABORATE_REQUEST = 'CR'
# JOINED_MEMBERSHIP = 'JM'
# COLLABORATE_REQUEST_ACCEPTED = 'CA'
# POST_MESSAGES = 'PM'
# POST_FINALIZED = 'PF'
# NEW_REVIEW = 'NR'
# NEW_DONATION = 'ND'


@task(name='check_if_pending_clearance_has_ended', max_retries=3)
def check_if_pending_clearance_has_ended():
    """Check if pending clearance has ended."""
    today = timezone.now()

    earnings = Earning.objects.filter(
        type__in=[Earning.DONATION_REVENUE],
        available_for_withdrawn_date__lt=today, setted_to_available_for_withdrawn=False)

    for earning in earnings:
        print(earning.amount)
        user = earning.user
        if user:
            pending_clearance_substracted = user.pending_clearance - earning.amount
            available_for_withdrawn_add = earning.amount
            if pending_clearance_substracted < Money(amount=0, currency="USD"):
                available_for_withdrawn_add = earning.amount + pending_clearance_substracted
                pending_clearance_substracted = 0

            user.pending_clearance = pending_clearance_substracted

            user.available_for_withdrawal += available_for_withdrawn_add

            user.save()

            earning.setted_to_available_for_withdrawn = True
            earning.save()
            return available_for_withdrawn_add.amount


@task(name='do_backup', max_retries=3)
def do_backup():
    management.call_command('dbbackup', '-z')
    print('Backup completed')
