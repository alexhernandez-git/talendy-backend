# Generated by Django 3.0.3 on 2021-05-13 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20210513_2124'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='draft_solution',
            field=models.TextField(blank=True, null=True),
        ),
    ]