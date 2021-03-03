# Generated by Django 3.0.3 on 2021-03-03 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_earning_transfer_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='earning',
            name='rate_date',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='earning',
            name='withdrawn_amount',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='earning',
            name='currency',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
    ]
