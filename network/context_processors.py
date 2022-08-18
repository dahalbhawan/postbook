from django.contrib.auth.models import User
from django.db.models import Count
from .models import Profile

def top_profiles(request):
    return {
        'top_profiles': Profile.objects.annotate(count=Count("followers")).order_by("-count")[0:10]
    }