

# Django
from django.db import models

# Utilities
from api.utils.models import CModel

import random
import string


class PostFolder(CModel):

    code = models.CharField(max_length=10, blank=True, null=True)
    name = models.CharField(max_length=100, default='')
    post = models.ForeignKey(
        'posts.Post', on_delete=models.CASCADE, related_name='post_folders')

    is_private = models.BooleanField(default=False)

    top_folder = models.ForeignKey(
        'posts.PostFolder', on_delete=models.CASCADE, related_name='post_folders_folder', null=True, blank=True)

    color = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):

        return '{}'.format(self.name)
