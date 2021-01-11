# Generated by Django 3.0.3 on 2021-01-11 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0005_auto_20210111_1915'),
        ('users', '0002_user_notifications'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='notifications',
            field=models.ManyToManyField(related_name='user_notifications', through='notifications.NotificationUser', to='notifications.Notification'),
        ),
    ]
