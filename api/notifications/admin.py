from django.contrib import admin

# Models
from api.notifications.models import Notification, NotificationUser

# Register your models here.


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    pass


@admin.register(NotificationUser)
class NotificationUserAdmin(admin.ModelAdmin):

    pass
