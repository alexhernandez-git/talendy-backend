from api.utils.models import CModel
from django.contrib.gis.db import models

# Models
from api.plans.models import Plan

from django.utils.text import slugify


class Portal(CModel):

    name = models.CharField('Portal name', max_length=140, unique=True)

    url = models.SlugField(max_length=40, unique=True)

    members = models.ManyToManyField("users.User", through="portals.PortalMember",
                                     through_fields=('portal', 'user'), verbose_name="room_participants")

    owner = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, related_name="portal_owner")

    about = models.TextField('about portal', max_length=500, null=True, blank=True)

    logo = models.ImageField(
        'portal logo',
        upload_to='portals/logos/',
        blank=True,
        null=True,
        max_length=500
    )

    # Config
    donations_enabled = models.BooleanField(default=False)

    # Users count
    members_count = models.IntegerField(default=0)
    active_members_count = models.IntegerField(default=0)

    basic_members_count = models.IntegerField(default=0)
    active_basic_members_count = models.IntegerField(default=0)

    manager_members_count = models.IntegerField(default=0)
    active_manager_members_count = models.IntegerField(default=0)

    admin_members_count = models.IntegerField(default=0)
    active_admin_members_count = models.IntegerField(default=0)

    posts_count = models.IntegerField(default=0)

    created_posts_count = models.IntegerField(default=0)

    created_active_posts_count = models.IntegerField(default=0)

    created_solved_posts_count = models.IntegerField(default=0)

    collaborated_posts_count = models.IntegerField(default=0)

    collaborated_active_posts_count = models.IntegerField(default=0)

    collaborated_solved_posts_count = models.IntegerField(default=0)

    plan_default_payment_method = models.CharField(max_length=100, blank=True, null=True)

    free_trial_invoiced = models.BooleanField(default=False)

    have_active_plan = models.BooleanField(
        'have active plan',
        default=False,
        help_text='Set to true have active plan.'
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

    is_oficial = models.BooleanField(default=False)

    def __str__(self):
        """Return username."""
        return '{}'.format(self.name)
