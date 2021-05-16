"""User model."""

# Django
from django.db.models.fields.related import ManyToManyField
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Models
from djmoney.models.fields import MoneyField

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
            'unique': 'Already exists a user with this email.'
        },
        blank=True,
    )
    username = models.CharField(
        max_length=150,
        unique=True,
    )

    about = models.TextField('about user', max_length=1000, null=True, blank=True)

    picture = models.ImageField(
        'profile picture',
        upload_to='users/pictures/',
        blank=True,
        null=True,
        max_length=500
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

    following = models.ManyToManyField("users.User", through="users.Follow", verbose_name="user_follow")

    # Estatistics

    following_count = models.IntegerField(default=0)

    connections_count = models.IntegerField(default=0)

    invitations_count = models.IntegerField(default=0)

    followed_count = models.IntegerField(default=0)

    posts_count = models.IntegerField(default=0)

    created_posts_count = models.IntegerField(default=0)

    created_active_posts_count = models.IntegerField(default=0)

    created_solved_posts_count = models.IntegerField(default=0)

    contributed_posts_count = models.IntegerField(default=0)

    contributed_active_posts_count = models.IntegerField(default=0)

    contributed_solved_posts_count = models.IntegerField(default=0)

    pending_notifications = models.BooleanField(default=False)

    pending_messages = models.BooleanField(default=False)

    karma_amount = models.IntegerField(default=1000)

    reputation = models.FloatField(
        blank=True, null=True
    )

    reviews_count = models.IntegerField(default=0)

    # Payments

    stripe_customer_id = models.CharField(
        max_length=100, blank=True, null=True)

    is_currency_permanent = models.BooleanField(default=False)
    currency = models.CharField(max_length=3, blank=True, null=True)
    default_payment_method = models.CharField(max_length=100, blank=True, null=True)

    # Paypal connect

    paypal_email = models.CharField(max_length=100, blank=True, null=True)

    # Notifications

    notifications = models.ManyToManyField(
        "notifications.Notification", through="notifications.NotificationUser", related_name="user_notifications"
    )

    # Donation Earnings
    donations_made_count = models.IntegerField(default=0)
    donations_received_count = models.IntegerField(default=0)

    net_income = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', default=0)
    withdrawn = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', default=0)
    available_for_withdrawal = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', default=0)
    pending_clearance = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', default=0)

    # Email notifications

    account_deactivated = models.BooleanField(default=False)

    is_online = models.BooleanField(default=False)

    def __str__(self):
        """Return username."""
        return '{} {}'.format(self.first_name, self.last_name)

    def save(self, **kwargs):
        try:
            this = User.objects.get(id=self.id)
            # import pdb
            # pdb.set_trace()
            if this.picture != self.picture:
                this.picture.delete(save=False)
        except:
            pass
        super(User, self).save(**kwargs)
