from django.contrib import admin

# Models
from api.posts.models import Post, KanbanList, KanbanCard

# Register your models here.


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Connection model admin."""

    list_display = ("id", "title", "user", "status")


@admin.register(KanbanList)
class KanbanListAdmin(admin.ModelAdmin):
    """Connection model admin."""

    list_display = ("id", "title")


@admin.register(KanbanCard)
class KanbanCardAdmin(admin.ModelAdmin):
    """Connection model admin."""

    list_display = ("id", "title")
