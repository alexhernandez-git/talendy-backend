"""User permissions."""

# Django REST Framework
from rest_framework.permissions import BasePermission
from rest_framework.generics import get_object_or_404

# Models
from api.posts.models import Post
from api.portals.models import PortalMember


class IsAdminOrManager(BasePermission):
    """Allow access only to objects owned by the requesting user."""

    def has_object_permission(self, request, view, obj):
        """Check obj and user are the same."""
        member = get_object_or_404(PortalMember, user=request.user, portal=obj)
        return member.role == PortalMember.ADMINISTRATOR or member.role == PortalMember.MANAGER


class IsAdmin(BasePermission):
    """Allow access only to objects owned by the requesting user."""

    def has_object_permission(self, request, view, obj):
        """Check obj and user are the same."""
        member = get_object_or_404(PortalMember, user=request.user, portal=obj)
        return member.role == PortalMember.ADMINISTRATOR
