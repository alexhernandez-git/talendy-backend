from django.contrib import admin

# Models
from api.chats.models import Chat, Message

# Register your models here.


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):

    pass


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):

    pass
