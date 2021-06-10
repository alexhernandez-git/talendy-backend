"""Users views."""

# Django
from api.users.models.karma_earnings import KarmaEarning
from django.http.response import HttpResponse
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from django.db.models import Q
from django.contrib.gis.db.models.functions import GeometryDistance

# Permissions
from rest_framework.permissions import IsAuthenticated
from api.posts.permissions import IsPostMember, IsPostOwner

# Models
from api.posts.models import Post
from api.users.models import Follow, User

# Serializers
from api.posts.serializers import (
    PostModelSerializer,
    CreatePostSeenBySerializer,
    ClearPostChatNotificationSerializer,
    RetrieveCollaborateRoomModelSerializer,
    UpdatePostSharedNotesSerializer,
    UpdatePostSolutionSerializer,
    FinalizePostSerializer,
    StopCollaboratingSerializer,
    UpdatePostWinnerKarmaSerializer,
    UpdateKanbanListOrderSerializer,
    UpdateKanbanCardOrderSerializer,
    UpdateKanbanCardOrderBetweenListsSerializer,
    UpdatePostDrawingSerializer,
    ClearPostDrawingSerializer
)

# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from api.posts.filters import PostFilter


class PostViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """User view set.

    Handle sign up, login and account verification.
    """

    queryset = Post.objects.all()
    lookup_field = "id"
    serializer_class = PostModelSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    filter_class = PostFilter
    search_fields = (
        "title",
        "text",
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    )

    def get_permissions(self):
        """Assign permissions based on action."""
        if self.action in ['create']:
            permissions = [IsAuthenticated]
        elif self.action in ['update', 'update_solution', 'update_karma_winner', 'finalize']:
            permissions = [IsPostOwner, IsAuthenticated]
        elif self.action in ['update_drawing', 'clear_drawing']:
            permissions = [IsAuthenticated, IsPostMember]
        else:
            permissions = []
        return [p() for p in permissions]

    def get_serializer_class(self):
        """Return serializer based on action."""

        if self.action == "retrieve_collaborate_room":
            return RetrieveCollaborateRoomModelSerializer
        return PostModelSerializer

    def get_queryset(self):
        """Restrict list to public-only."""
        queryset = Post.objects.all()

        if self.action == "list":
            queryset = Post.objects.filter(
                members_count__lte=5)

        elif self.action == "list_most_karma_posts":
            queryset = Post.objects.filter(members_count__lte=5).order_by('-karma_offered')

        elif self.action == "list_followed_users_posts":
            if self.request.user.id:

                user = self.request.user
                queryset = Post.objects.filter(
                    user__id__in=Follow.objects.filter(from_user=user).values_list(
                        'followed_user'), members_count__lte=5)
            else:
                queryset = Post.objects.none()
        elif self.action == "list_nearest_posts":
            if self.request.user.id and self.request.user.id:
                user = self.request.user
                if user.geolocation:

                    queryset = queryset.filter(members_count__lte=5).exclude(user=user.id).annotate(
                        distance=GeometryDistance("user__geolocation", user.geolocation)).order_by('distance')
                else:
                    queryset = Post.objects.none()
            else:
                queryset = Post.objects.none()

        elif self.action == "list_my_posts":
            user = self.request.user
            queryset = Post.objects.filter(user=user)

        elif self.action == "list_my_active_posts":
            user = self.request.user
            queryset = Post.objects.filter(user=user, status=Post.ACTIVE)

        elif self.action == "list_my_solved_posts":
            user = self.request.user
            queryset = Post.objects.filter(user=user, status=Post.SOLVED)

        elif self.action == "list_collaborated_posts":
            user = self.request.user
            queryset = Post.objects.filter(members=user).exclude(user=user)

        elif self.action == "list_collaborated_active_posts":
            user = self.request.user
            queryset = Post.objects.filter(members=user, status=Post.ACTIVE).exclude(user=user)

        elif self.action == "list_collaborated_solved_posts":
            user = self.request.user
            queryset = Post.objects.filter(members=user, status=Post.SOLVED).exclude(user=user)

        elif self.action == "list_user_posts":
            user = get_object_or_404(User, id=self.kwargs['id'])
            queryset = Post.objects.filter(Q(user=user) | Q(members=user)).distinct()

        elif self.action == "list_user_created":
            user = get_object_or_404(User, id=self.kwargs['id'])
            queryset = Post.objects.filter(user=user)

        elif self.action == "list_user_collaborated":
            user = get_object_or_404(User, id=self.kwargs['id'])
            queryset = Post.objects.filter(members=user).exclude(user=user)

        return queryset

    @action(detail=False, methods=['get'])
    def list_most_karma_posts(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def list_followed_users_posts(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def list_nearest_posts(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def list_my_posts(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def list_my_active_posts(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def list_my_solved_posts(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def list_collaborated_posts(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def list_collaborated_active_posts(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def list_collaborated_solved_posts(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def list_user_posts(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def list_user_created(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def list_user_collaborated(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def retrieve_collaborate_room(self, request, *args, **kwargs):
        instance = self.get_object()
        # Create seen by
        createSeenSerializer = CreatePostSeenBySerializer(
            data={}, context={"request": request, "post": instance}
        )
        is_valid = createSeenSerializer.is_valid(raise_exception=False)
        if is_valid:
            createSeenSerializer.save()

        # Clear post notifications
        clearChatNotification = ClearPostChatNotificationSerializer(
            instance,
            data={},
            context={"request": request, "post": instance},
            partial=True
        )
        is_valid = clearChatNotification.is_valid(raise_exception=False)
        if is_valid:
            clearChatNotification.update(instance, request)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = PostModelSerializer(data=request.data, context={
                                         "request": request, "images": request.data.getlist('images')})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        post = self.get_object()

        partial = request.method == 'PATCH'

        serializer = PostModelSerializer(
            post, data=request.data,
            context={"request": request, "images": request.data.getlist('images'),
                     "current_images": request.data['current_images']},
            partial=partial)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def update_shared_notes(self, request, *args, **kwargs):
        post = self.get_object()

        partial = request.method == 'PATCH'

        serializer = UpdatePostSharedNotesSerializer(
            post,
            data=request.data,
            context={"request": request},
            partial=partial)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def update_drawing(self, request, *args, **kwargs):
        post = self.get_object()

        partial = request.method == 'PATCH'

        serializer = UpdatePostDrawingSerializer(
            post,
            data=request.data,
            context={"request": request},
            partial=partial)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def clear_drawing(self, request, *args, **kwargs):
        post = self.get_object()

        partial = request.method == 'PATCH'

        serializer = ClearPostDrawingSerializer(
            post,
            data=request.data,
            context={"request": request},
            partial=partial)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def update_kanban_list_order(self, request, *args, **kwargs):
        post = self.get_object()

        partial = request.method == 'PATCH'

        serializer = UpdateKanbanListOrderSerializer(
            post,
            data=request.data,
            context={"request": request},
            partial=partial)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'])
    def update_kanban_card_order(self, request, *args, **kwargs):
        post = self.get_object()

        partial = request.method == 'PATCH'

        serializer = UpdateKanbanCardOrderSerializer(
            post,
            data=request.data,
            context={"request": request},
            partial=partial)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'])
    def update_kanban_card_between_lists_order(self, request, *args, **kwargs):
        post = self.get_object()

        partial = request.method == 'PATCH'

        serializer = UpdateKanbanCardOrderBetweenListsSerializer(
            post,
            data=request.data,
            context={"request": request},
            partial=partial)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'])
    def update_solution(self, request, *args, **kwargs):
        post = self.get_object()

        partial = request.method == 'PATCH'

        serializer = UpdatePostSolutionSerializer(
            post,
            data=request.data,
            context={"request": request},
            partial=partial)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def update_karma_winner(self, request, *args, **kwargs):
        post = self.get_object()

        partial = request.method == 'PATCH'

        serializer = UpdatePostWinnerKarmaSerializer(
            post,
            data=request.data,
            context={"request": request},
            partial=partial)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def stop_collaborating(self, request, *args, **kwargs):
        post = self.get_object()

        partial = request.method == 'PATCH'

        serializer = StopCollaboratingSerializer(
            post,
            data=request.data,
            context={"request": request},
            partial=partial)

        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        data = RetrieveCollaborateRoomModelSerializer(post).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def finalize(self, request, *args, **kwargs):
        post = self.get_object()

        partial = request.method == 'PATCH'

        serializer = FinalizePostSerializer(
            post,
            data=request.data,
            context={"request": request},
            partial=partial)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        user = instance.user

        if instance.members.all().count() > 1:

            return Response(
                {"message": "You cannot delete a post that already has members"},
                status=status.HTTP_400_BAD_REQUEST)

        # Update statistics on post deletion
        user.posts_count -= 1
        user.created_posts_count -= 1
        if instance.status == Post.ACTIVE:
            user.created_active_posts_count -= 1
        elif instance.status == Post.SOLVED:
            user.created_solved_posts_count -= 1
        user.karma_amount = user.karma_amount + instance.karma_offered
        KarmaEarning.objects.create(user=user, amount=instance.karma_offered, type=KarmaEarning.EARNED)

        user.save()

        for member in instance.members.all().exclude(id=user.id):

            member.posts_count -= 1
            member.collaborated_posts_count -= 1
            if instance.status == Post.ACTIVE:
                member.collaborated_active_posts_count -= 1
            elif instance.status == Post.SOLVED:
                member.collaborated_solved_posts_count -= 1

            member.save()

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
