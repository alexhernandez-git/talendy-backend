"""User permissions."""

# Django REST Framework
from rest_framework.permissions import BasePermission

# Models
from api.posts.models import Post


class IsPostOwner(BasePermission):
    """Allow access only to objects owned by the requesting user."""

    def has_object_permission(self, request, view, obj):
        """Check obj and user are the same."""

        return request.user == obj.user


class IsPostMember(BasePermission):
    """Allow access only to objects owned by the requesting user."""

    def has_object_permission(self, request, view, obj):
        """Check obj and user are the same."""

        return Post.objects.filter(members=request.user).exists()


class IsPostOwnerPostMembers(BasePermission):
    """Allow access only to objects owned by the requesting user."""

    def has_object_permission(self, request, view, obj):
        """Check obj and user are the same."""

        return request.user == self.post.user
