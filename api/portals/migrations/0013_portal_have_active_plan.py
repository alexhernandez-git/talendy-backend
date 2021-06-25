# Generated by Django 3.0.3 on 2021-06-23 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0012_auto_20210623_1741'),
    ]

    operations = [
        migrations.AddField(
            model_name='portal',
            name='have_active_plan',
            field=models.BooleanField(default=False, help_text='Set to true have active plan.', verbose_name='have active plan'),
        ),
    ]
