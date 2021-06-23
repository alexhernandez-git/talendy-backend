# Generated by Django 3.0.3 on 2021-06-22 14:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0007_auto_20210622_1511'),
        ('chats', '0002_auto_20210519_1221'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='portal',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='portals.Portal'),
        ),
    ]