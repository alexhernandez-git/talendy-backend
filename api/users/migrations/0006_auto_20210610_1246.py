# Generated by Django 3.0.3 on 2021-06-10 10:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20210608_2119'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='karma_earned',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='karma_spent',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='karma_amount',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='KarmaEarning',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('type', models.CharField(choices=[('EA', 'Earned'), ('SP', 'Spent')], max_length=2)),
                ('amount', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
    ]