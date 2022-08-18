from django.db.models.signals import post_save

from .models import Profile, User

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(receiver=create_user_profile, sender=User)