# Generated by Django 3.0.3 on 2021-06-04 16:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0006_auto_20210604_0007'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostFolder',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('code', models.CharField(blank=True, max_length=10, null=True)),
                ('name', models.CharField(default='', max_length=100)),
                ('is_private', models.BooleanField(default=False)),
                ('color', models.CharField(blank=True, max_length=50, null=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_folders', to='posts.Post')),
                ('top_folder', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_folders_folder', to='posts.PostFolder')),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PostFile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('code', models.CharField(blank=True, max_length=10, null=True)),
                ('name', models.CharField(default='', max_length=100)),
                ('is_private', models.BooleanField(default=False)),
                ('file', models.FileField(max_length=500, upload_to='posts/resources/files/')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_files', to='posts.Post')),
                ('shared_users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('top_folder', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_files_folder', to='posts.PostFolder')),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
    ]