# Generated by Django 3.0.3 on 2021-05-09 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20210508_0025'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='solution',
            field=models.TextField(blank=True, null=True),
        ),
    ]
