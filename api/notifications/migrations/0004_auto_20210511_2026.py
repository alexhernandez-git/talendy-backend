# Generated by Django 3.0.3 on 2021-05-11 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_post_shared_notes'),
        ('notifications', '0003_auto_20210511_1922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='post_messages',
            field=models.ManyToManyField(blank=True, related_name='notifications_post_messages', to='posts.PostMessage'),
        ),
    ]