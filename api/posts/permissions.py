

# Django REST Framework
from rest_framework.permissions import BasePermission

# Models
from api.posts.models import Post


class IsPostOwner(BasePermission):

    def has_object_permission(self, request, view, obj):

        return request.user == obj.user


class IsPostMember(BasePermission):

    def has_object_permission(self, request, view, obj):

        return Post.objects.filter(members=request.user).exists()


class IsPostOwnerPostMembers(BasePermission):

    def has_object_permission(self, request, view, obj):

        return request.user == self.post.user
