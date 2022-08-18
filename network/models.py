from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': '' if not self.email else self.email,
        }

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(blank=True, null=True)
    followers = models.ManyToManyField(User, blank=True, related_name="following_profiles")

    @property
    def followers_profiles(self):
        return [follower.profile for follower in self.followers.all()]

    def serialize(self):
        return {
            'id': self.id,
            'user': self.user.id,
            'followers': [user.serialize() for user in self.followers.all()],
        }

    def __str__(self):
        return self.user.username

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name="posts")
    text = models.CharField(max_length=255, null=False, blank=False)
    likers = models.ManyToManyField(User, blank=True)
    is_edited = models.BooleanField(default=False)
    last_edited_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        ordering = ["-created_at", "-last_edited_at"]

    @property
    def like_count(self):
        return self.likers.count()

    @property
    def likers_profiles(self):
        return [liker.profile for liker in self.likers]

    def serialize(self):
        return {
            'id': self.id,
            'user': self.user.id,
            'text': self.text,
            'likers': [user.serialize() for user in self.likers.all()],
            'is_edited': self.is_edited,
            'last_edited_at': self.last_edited_at,
            'created_at': self.created_at
        }

    def __str__(self):
        return self.user.username
