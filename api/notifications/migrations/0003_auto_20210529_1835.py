# Generated by Django 3.0.3 on 2021-05-29 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_auto_20210519_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('ME', 'Messages'), ('NI', 'New invitation'), ('NC', 'New connection'), ('CR', 'New collaborate request'), ('JM', 'Joined membership'), ('CA', 'Collaborate request accepted'), ('PM', 'Post messages'), ('PF', 'Post finalized'), ('NR', 'New review'), ('ND', 'New donation'), ('CF', 'Post created by a followed')], max_length=2),
        ),
    ]