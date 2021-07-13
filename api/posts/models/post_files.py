

# Django
from django.db import models

# Utilities
from api.utils.models import CModel

import random
import string

import os


class PostFile(CModel):

    code = models.CharField(max_length=10, blank=True, null=True)
    name = models.CharField(max_length=100, default='')
    post = models.ForeignKey(
        'posts.Post', on_delete=models.CASCADE, related_name='post_files')

    is_private = models.BooleanField(default=False)

    file = models.FileField(
        upload_to='posts/resources/files/',
        max_length=500,
        null=True, blank=True
    )
    top_folder = models.ForeignKey(
        'posts.PostFolder', on_delete=models.CASCADE, related_name='post_files_folder', null=True, blank=True)

    shared_users = models.ManyToManyField(
        'users.User'
    )
    size = models.IntegerField(default=0)

    def __str__(self):

        return '{}'.format(self.name)

    def save(self, **kwargs):

        try:
            this = PostFile.objects.get(id=self.id)
            if this.file != self.file:
                this.file.delete(save=False)
        except:
            pass

        super(PostFile, self).save(**kwargs)
