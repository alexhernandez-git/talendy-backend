# Generated by Django 3.0.3 on 2021-03-15 17:39

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20210315_1815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='earning',
            name='available_for_withdrawn_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 29, 17, 39, 21, 795659, tzinfo=utc), help_text='Date time on pending clearance ends.', verbose_name='pending clearance expiration at'),
        ),
    ]
