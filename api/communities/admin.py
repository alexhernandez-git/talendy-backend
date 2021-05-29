from django.contrib import admin

# Models
from api.communities.models import Community

# Register your models here.


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    """Community model admin."""
