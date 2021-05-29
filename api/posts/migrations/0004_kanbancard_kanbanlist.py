# Generated by Django 3.0.3 on 2021-05-29 22:43

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_post_karma_winner'),
    ]

    operations = [
        migrations.CreateModel(
            name='KanbanList',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('order', models.IntegerField()),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='posts.Post')),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='KanbanCard',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('order', models.IntegerField()),
                ('list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='posts.KanbanList')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]