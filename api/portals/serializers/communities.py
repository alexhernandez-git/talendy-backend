

# Django REST Framework
from rest_framework import serializers

# Django


# Serializers


# Models
from api.portals.models import Community


class CommunityModelSerializer(serializers.ModelSerializer):

    class Meta:

        model = Community
        fields = (
            "id",
            "name",
            "posts_count",
            "active_posts_count",
            "solved_posts_count",
        )

        read_only_fields = ("id", "posts_count", "active_posts_count", "solved_posts_count")

    def validate(self, data):
        return data

    def create(self, validated_data):
        portal = self.context['portal']

        community = Community.objects.create(**validated_data, portal=portal)

        portal.communities_count += 1
        portal.save()

        return community
