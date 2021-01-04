from django.contrib import admin

# Models
from api.chat.models import Chat

# Register your models here.


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    """Chat model admin."""