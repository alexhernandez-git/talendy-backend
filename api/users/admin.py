

# Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Models
from api.users.models import User, Earning, Follow, UserLoginActivity, Connection, Blacklist


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):

    list_display = ("id", "from_member", "followed_member")


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):

    list_display = ("id", "requester", "addressee")


class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + ((None,
                                        {
                                            "fields":
                                            ("is_verified", "is_online", "posts_count", "created_posts_count",
                                             "created_active_posts_count", "created_solved_posts_count",
                                             "collaborated_posts_count", "collaborated_active_posts_count",
                                             "collaborated_solved_posts_count", "account_deactivated",
                                             "email_notifications_allowed", "country", "country_name", "region",
                                             "region_name",
                                             "city",
                                             "zip",
                                             "geolocation", "karma_amount")}),)

    list_display = ("email", "first_name", "last_name", "is_staff",
                    "is_client", "is_online", "country")
    list_filter = (
        "is_client",
        "is_staff",
        "created",
        "modified",
        "is_online",
        "account_deactivated",

    )


@admin.register(Earning)
class EarningAdmin(admin.ModelAdmin):
    pass


@admin.register(UserLoginActivity)
class UserLoginActivityAdmin(admin.ModelAdmin):

    list_display = ("login_username", "created")


@admin.register(Blacklist)
class BlacklistAdmin(admin.ModelAdmin):

    list_display = ("IP", "created")


admin.site.register(User, CustomUserAdmin)
