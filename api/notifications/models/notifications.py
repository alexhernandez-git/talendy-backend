from api.utils.models import CModel
from django.db import models


class NotificationUser(CModel):

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    notification = models.ForeignKey("notifications.Notification", on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)


class Notification(CModel):

    MESSAGES = 'ME'
    NEW_INVITATION = 'NI'
    NEW_CONNECTION = 'NC'
    NEW_COLLABORATE_REQUEST = 'CR'
    JOINED_MEMBERSHIP = 'JM'
    COLLABORATE_REQUEST_ACCEPTED = 'CA'
    POST_MESSAGES = 'PM'
    POST_FINALIZED = 'PF'
    NEW_REVIEW = 'NR'
    NEW_DONATION = 'ND'
    TYPE_CHOICES = [
        (MESSAGES, 'Messages'),
        (NEW_INVITATION, 'New invitation'),
        (NEW_CONNECTION, 'New connection'),
        (NEW_COLLABORATE_REQUEST, 'New collaborate request'),
        (JOINED_MEMBERSHIP, 'Joined membership'),
        (COLLABORATE_REQUEST_ACCEPTED, 'Collaborate request accepted'),
        (POST_MESSAGES, 'Post messages'),
        (POST_FINALIZED, 'Post finalized'),
        (NEW_REVIEW, 'New review'),
        (NEW_DONATION, 'New donation'),
    ]
    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
    )

    # MESSAGES
    messages = models.ManyToManyField(
        "chats.Message", blank=True, related_name="notifications_messages"
    )
    chat = models.ForeignKey("chats.Chat", on_delete=models.CASCADE, null=True)

    # CONNECTIONS
    connection = models.ForeignKey("users.Connection", on_delete=models.CASCADE, null=True)

    # COLLABORATE_REQUESTS
    collaborate_request = models.ForeignKey("posts.CollaborateRequest", on_delete=models.CASCADE, null=True)

    # JOINED_MEMBERSHIP
    member_joined = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True, related_name="member_joined")

    # POST_MESSAGES
    post_messages = models.ManyToManyField(
        "posts.PostMessage", blank=True, related_name="notifications_post_messages"
    )

    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, null=True)

    # NEW_REVIEW
    review = models.ForeignKey("users.Review", on_delete=models.CASCADE, null=True)

    # NEW_DONATION
    donation = models.ForeignKey("donations.Donation", on_delete=models.CASCADE, null=True)

    actor = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
