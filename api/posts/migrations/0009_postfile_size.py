# Generated by Django 3.0.3 on 2021-06-06 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_post_files_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='postfile',
            name='size',
            field=models.IntegerField(default=0),
        ),
    ]
