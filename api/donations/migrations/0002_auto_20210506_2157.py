# Generated by Django 3.0.3 on 2021-05-06 19:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('donations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='from_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_user_donaiton', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='donation',
            name='to_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_user_donation', to=settings.AUTH_USER_MODEL),
        ),
    ]