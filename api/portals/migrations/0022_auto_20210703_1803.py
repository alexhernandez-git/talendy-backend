# Generated by Django 3.0.3 on 2021-07-03 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0021_auto_20210703_1504'),
    ]

    operations = [
        migrations.AddField(
            model_name='portalmember',
            name='karma_earned_by_join_portal',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='portalmember',
            name='karma_earned_by_posts',
            field=models.IntegerField(default=0),
        ),
    ]
