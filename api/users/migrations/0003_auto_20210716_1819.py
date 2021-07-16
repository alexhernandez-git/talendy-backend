# Generated by Django 3.0.3 on 2021-07-16 16:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0004_auto_20210713_1320'),
        ('users', '0002_follow_portal'),
    ]

    operations = [
        migrations.AddField(
            model_name='connection',
            name='portal',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='portals.Portal'),
        ),
        migrations.AlterField(
            model_name='connection',
            name='addressee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addressee', to='portals.PortalMember'),
        ),
        migrations.AlterField(
            model_name='connection',
            name='requester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requester', to='portals.PortalMember'),
        ),
        migrations.AlterField(
            model_name='follow',
            name='followed_member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_followed_member', to='portals.PortalMember'),
        ),
        migrations.AlterField(
            model_name='follow',
            name='from_member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_follow_member', to='portals.PortalMember'),
        ),
    ]