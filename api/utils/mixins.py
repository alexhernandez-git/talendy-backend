"""Add circle mixin abstract."""

# Django REST Framework
from rest_framework import mixins, viewsets
from rest_framework.generics import get_object_or_404

# Models
from api.chats.models import Chat
from api.posts.models import Post, KanbanList

# Utils


class AddListMixin(viewsets.GenericViewSet):
    """Add circle mixin

    Manages adding a circle object to views
    that require it.
    """

    def dispatch(self, request, *args, **kwargs):
        """Return the normal dispatch but adds the circle model."""

        id = self.kwargs["slug_id"]

        self.post_object = get_object_or_404(Post, id=id)

        list_id = self.kwargs["list_slug_id"]

        self.kanban_list = get_object_or_404(KanbanList, id=list_id)

        return super(AddListMixin, self).dispatch(request, *args, **kwargs)


class AddPostMixin(viewsets.GenericViewSet):
    """Add circle mixin

    Manages adding a circle object to views
    that require it.
    """

    def dispatch(self, request, *args, **kwargs):
        """Return the normal dispatch but adds the circle model."""

        id = self.kwargs["slug_id"]

        self.post_object = get_object_or_404(Post, id=id)

        return super(AddPostMixin, self).dispatch(request, *args, **kwargs)


class AddChatMixin(viewsets.GenericViewSet):
    """Add circle mixin

    Manages adding a circle object to views
    that require it.
    """

    def dispatch(self, request, *args, **kwargs):
        """Return the normal dispatch but adds the circle model."""

        id = self.kwargs["slug_id"]

        self.chat = get_object_or_404(Chat, id=id)

        return super(AddChatMixin, self).dispatch(request, *args, **kwargs)
