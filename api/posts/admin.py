from django.contrib import admin

# Models
from api.posts.models import Post

# Register your models here.


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Connection model admin."""

    list_display = ("id", "title", "user", "status")
