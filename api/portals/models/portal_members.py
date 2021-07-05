from api.utils.models import CModel
from django.contrib.gis.db import models

from django.utils.text import slugify

from django.core.validators import RegexValidator


class PortalMember(CModel):

    portal = models.ForeignKey('portals.Portal', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True)

    # Creator
    creator = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name="member_creator")

    # Member info \ This info will be traspased to the user model
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    email = models.EmailField(
        'email address',
        unique=False,
        blank=True,
    )

    notes = models.TextField('notes of member', max_length=1000, null=True, blank=True)

    picture = models.ImageField(
        'profile picture',
        upload_to='users/pictures/',
        blank=True,
        null=True,
        max_length=500
    )

    password = models.CharField(max_length=128, blank=True, null=True)

    initial_karma_amount = models.IntegerField(default=0)

    # Statistics

    karma_amount = models.IntegerField(default=0)

    karma_refunded = models.IntegerField(default=0)

    karma_earned = models.IntegerField(default=0)

    karma_earned_by_posts = models.IntegerField(default=0)

    karma_earned_by_join_portal = models.IntegerField(default=0)

    karma_earned_by_donations = models.IntegerField(default=0)

    karma_spent = models.IntegerField(default=0)

    karma_ratio = models.FloatField(default=0)

    following_count = models.IntegerField(default=0)

    connections_count = models.IntegerField(default=0)

    invitations_count = models.IntegerField(default=0)

    followed_count = models.IntegerField(default=0)

    posts_count = models.IntegerField(default=0)

    created_posts_count = models.IntegerField(default=0)

    created_active_posts_count = models.IntegerField(default=0)

    created_solved_posts_count = models.IntegerField(default=0)

    collaborated_posts_count = models.IntegerField(default=0)

    collaborated_active_posts_count = models.IntegerField(default=0)

    collaborated_solved_posts_count = models.IntegerField(default=0)

    # Make the user active before the login invitation
    is_active = models.BooleanField(default=False)

    ADMIN = 'AD'
    MANAGER = 'MA'
    BASIC = 'BA'
    MEMBER_TYPE = [
        (ADMIN, 'Administrator'),
        (MANAGER, 'Manager'),
        (BASIC, 'Basic'),
    ]

    role = models.CharField(
        max_length=2,
        choices=MEMBER_TYPE,
        default=BASIC
    )
