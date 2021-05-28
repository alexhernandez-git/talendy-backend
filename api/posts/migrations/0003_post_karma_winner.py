# Generated by Django 3.0.3 on 2021-05-28 13:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20210519_1221'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='karma_winner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='karma_winner', to='posts.PostMember'),
        ),
    ]
