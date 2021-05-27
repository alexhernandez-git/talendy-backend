from django_filters.filters import BooleanFilter, ChoiceFilter
from rest_framework import filters
import django_filters

# Django
from django.contrib.gis.db.models.functions import GeometryDistance

# Models
from api.posts.models import Post


class PostFilter(django_filters.FilterSet):

    class Meta:
        model = Post
        fields = ['community', 'status']
