"""User model."""

# Django
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Utilities
from api.utils.models import CModel


class User(CModel, AbstractUser):
    """User model.
    Extend from Django's Abstract User, change the username field
    to email and add some extra fields.
    """

    email = models.EmailField(
        'email address',
        unique=True,
        error_messages={
            'unique': 'Ya existe un usuario con este email.'
        },
        blank=True,
    )
    username = models.CharField(
        max_length=150,
        unique=True,
    )

    phone_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: +999999999. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex], max_length=17, blank=True)

    # USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    is_client = models.BooleanField(
        'client',
        default=True,
        help_text=(
            'Help easily distinguish users and perform queries. '
            'Clients are the main type of user.'
        )
    )

    is_verified = models.BooleanField(
        'verified',
        default=False,
        help_text='Set to true when the user have verified its email address.'
    )

    country = models.CharField(max_length=2, blank=True, null=True)

    # Is seller
    is_seller = models.BooleanField(
        'seller',
        default=False,
        help_text='Set to true when the user have a seller account.'
    )

    SELLER = 'SE'
    BUYER = 'BU'
    TYPE_CHOICES_CURRENT_VIEW = [
        (SELLER, 'Seller'),
        (BUYER, 'Buyer'),
    ]
    current_view = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES_CURRENT_VIEW,
        default=SELLER
    )


    is_free_trial = models.BooleanField(
        'free trial',
        default=False,
        help_text='Set to true when the seller is in free trial.'
    )

    passed_free_trial_once = models.BooleanField(
        'passed free trial',
        default=False,
        help_text='Set to true when the seller alreay passed free trial once.'
    )

    free_trial_expiration = models.DateTimeField(
        'free trial expiration at',
        help_text='Date time on the free tiral expiration.',
        null=True, blank=True,
    )

    have_active_plan = models.BooleanField(
        'have active plan subscription',
        default=False,
        help_text='Set to true when the user have a active plan subscription.'
    )

    # Plan
    BASIC = 'BA'
    TYPE_CHOICES = [
        (BASIC, 'Basic'),
    ]
    plan_type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
    )

    # Payments
    stripe_customer_id = models.CharField(
        max_length=100, blank=True, null=True)

    currency = models.CharField(max_length=3, blank=True, null=True)

    # Stripe connect
    stripe_account_id = models.CharField(max_length=100, blank=True, null=True)
    money_balance = models.FloatField(blank=True, null=True)

    def __str__(self):
        """Return username."""
        return '{} {}'.format(self.first_name, self.last_name)
