
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("following-posts", views.following_view, name="following"),
    path("posts/create", views.create_post, name="create-post"),

    path("profile/update", views.update_profile, name="update-profile"),
    path("profile/<str:pk>/follow", views.follow_profile, name="follow-profile"),
    path("users/profile/<str:pk>", views.profile_view, name="user-profile"),

    path("posts/<str:pk>", views.get_post, name="post"),
    path("posts/update/<str:pk>", views.update_post, name="update-post"),
    path("posts/<str:pk>/like", views.like_post, name="like-post"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)