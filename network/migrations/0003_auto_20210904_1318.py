# Generated by Django 3.1.1 on 2021-09-04 13:18

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_post_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='followers',
            field=models.ManyToManyField(blank=True, null=True, related_name='following_profiles', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='profile',
            name='following',
            field=models.ManyToManyField(blank=True, null=True, related_name='follower_profiles', to=settings.AUTH_USER_MODEL),
        ),
    ]
