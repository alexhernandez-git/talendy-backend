

# Django REST Framework
from rest_framework.permissions import BasePermission
from rest_framework.generics import get_object_or_404

# Models
from api.posts.models import Post
from api.portals.models import PortalMember


class IsAdminOrManagerPortal(BasePermission):

    def has_object_permission(self, request, view, obj):

        member = get_object_or_404(PortalMember, user=request.user, portal=obj)
        return member.role == PortalMember.ADMIN or member.role == PortalMember.MANAGER


class IsAdminOrManager(BasePermission):

    def has_object_permission(self, request, view, obj):
        member = get_object_or_404(PortalMember, user=request.user, portal=view.portal)
        return member.role == PortalMember.ADMIN or member.role == PortalMember.MANAGER


class IsAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):

        member = get_object_or_404(PortalMember, user=request.user, portal=obj)
        return member.role == PortalMember.ADMIN
