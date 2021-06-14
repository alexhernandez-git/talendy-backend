# Generated by Django 3.0.3 on 2021-06-14 14:19

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('type', models.CharField(choices=[('SI', 'Silver'), ('GO', 'Gold'), ('PL', 'Platinum')], max_length=2)),
                ('interval', models.CharField(choices=[('MO', 'Monthly'), ('YE', 'Yearly')], default='MO', max_length=2)),
                ('active_users_amount', models.IntegerField()),
                ('unit_amount', models.FloatField(blank=True, null=True)),
                ('currency', models.CharField(blank=True, max_length=3, null=True)),
                ('price_label', models.CharField(blank=True, max_length=100, null=True)),
                ('stripe_price_id', models.CharField(blank=True, max_length=100, null=True)),
                ('stripe_product_id', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
    ]
