# Generated by Django 3.0.3 on 2021-06-15 15:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='portal',
            old_name='users',
            new_name='members',
        ),
    ]