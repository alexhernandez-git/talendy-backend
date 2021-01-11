from django.contrib import admin

# Models
from api.notifications.models import Notification, NotificationUser

# Register your models here.


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification model admin."""
    pass


@admin.register(NotificationUser)
class NotificationUserAdmin(admin.ModelAdmin):
    """Notification user model admin."""
    pass
