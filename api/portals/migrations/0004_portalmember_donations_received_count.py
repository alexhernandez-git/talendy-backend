# Generated by Django 3.0.3 on 2021-07-08 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0003_portalmember_donations_made_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='portalmember',
            name='donations_received_count',
            field=models.IntegerField(default=0),
        ),
    ]
