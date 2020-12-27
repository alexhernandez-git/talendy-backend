# Generated by Django 3.0.3 on 2020-12-27 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_have_active_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='current_view',
            field=models.CharField(choices=[('SE', 'Seller'), ('BU', 'Buyer')], default='SE', max_length=2),
        ),
    ]
