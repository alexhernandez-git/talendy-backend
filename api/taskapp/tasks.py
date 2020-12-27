"""Celery tasks."""

# Django
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone


# Celery
from celery.decorators import task

# Utilities
import jwt
import time
from datetime import timedelta

import re

