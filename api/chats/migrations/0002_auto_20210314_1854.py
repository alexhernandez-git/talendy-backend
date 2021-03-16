# Generated by Django 3.0.3 on 2021-03-14 17:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chats', '0001_initial'),
        ('activities', '0002_auto_20210314_1854'),
    ]

    operations = [
        migrations.AddField(
            model_name='seenby',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seen_by_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='participant',
            name='participant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='participant',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chats.Chat'),
        ),
        migrations.AddField(
            model_name='message',
            name='activity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='activities.Activity'),
        ),
        migrations.AddField(
            model_name='message',
            name='chat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chats.Chat'),
        ),
        migrations.AddField(
            model_name='message',
            name='sent_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chat',
            name='last_message',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='last_message', to='chats.Message'),
        ),
        migrations.AddField(
            model_name='chat',
            name='participants',
            field=models.ManyToManyField(through='chats.Participant', to=settings.AUTH_USER_MODEL, verbose_name='room_participants'),
        ),
    ]
