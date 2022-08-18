import json
from datetime import datetime
from functools import reduce
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponseRedirect
from django.http.response import HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import Post, User, Profile
from .forms import UserUpdateForm, ProfileUpdateForm


POSTS_PER_PAGE = 10

def index(request):
    posts = Post.objects.all()

    paginator = Paginator(posts, POSTS_PER_PAGE)
    pages = paginator.num_pages
    page_num = request.GET.get('page')

    if not page_num or int(page_num) <= 0:
        page_num = 1
    if page_num and int(page_num) >= pages:
        page_num = pages
    page_posts = paginator.get_page(page_num)

    context = {
        'posts': page_posts,
        'pages': pages,
        'current_page': page_num,
    }
    return render(request, "network/index.html", context)


@login_required(login_url='login')
def following_view(request):
    user = request.user

    following_users = [profile.user for profile in user.following_profiles.all()]

    # all the post by users who the authenticated user is following
    if not len(following_users) == 0:
        posts = reduce(lambda x, y: x + y, [list(user.posts.all()) for user in following_users])
    else:
        posts = []

    paginator = Paginator(posts, POSTS_PER_PAGE)
    pages = paginator.num_pages
    page_num = request.GET.get('page')

    if not page_num or int(page_num) <= 0:
        page_num = 1
    if page_num and int(page_num) >= pages:
        page_num = pages
    page_posts = paginator.get_page(page_num)
    
    context = {
        'posts': page_posts,
        'pages': pages,
        'current_page': page_num,
        'is_following_page': True,
    }

    return render(request, "network/index.html", context)

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")   

def profile_view(request, pk):
    user = request.user
    profile_user = User.objects.get(pk=pk)
    posts = Post.objects.filter(user=profile_user)
    profile = Profile.objects.get(user=profile_user)

    is_following = (request.user.is_authenticated) and (profile_user.profile in user.following_profiles.all())
    has_permission = user == profile_user

    paginator = Paginator(posts, POSTS_PER_PAGE)
    pages = paginator.num_pages
    page_num = request.GET.get('page')

    if not page_num or int(page_num) <= 0:
        page_num = 1
    if page_num and int(page_num) >= pages:
        page_num = pages
    page_posts = paginator.get_page(page_num)

    context = {
        'has_permission': has_permission,
        'profile': profile,
        'posts': page_posts,
        'is_following': is_following,
        'pages': pages,
        'current_page': page_num,
    }

    return render(request, 'network/profile.html', context)

@csrf_exempt
@login_required(login_url='login')
def get_post(request, pk):
    user = request.user
    post = Post.objects.get(pk=pk)

    if user == post.user:
        return JsonResponse({'post': post.serialize()}, status=200)
    
    return HttpResponseBadRequest()

@login_required(login_url='login')
def create_post(request):
    user = request.user

    if request.method == 'POST':
        text = request.POST['post-text']
        Post.objects.create(user=user, text=text)
    
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    return JsonResponse({'error': 'Something went wrong. Post was not created.'}, status=400)

@csrf_exempt
@login_required(login_url='login')
def update_post(request, pk):
    user = request.user
    post = Post.objects.get(pk=pk)

    # check the method and if the user is the owner of post or not
    if request.method == 'PUT' and user == post.user:
        data = json.loads(request.body)
       
        post.text = data['text']
        post.is_edited = True
        post.last_edited_at = datetime.now()
        post.save()

        return JsonResponse({'success': 'Post edited successfully.', 'data': post.serialize()}, status=200)

    return JsonResponse({'error': 'Something went wrong. Post was not updated.'}, status=400)

@csrf_exempt
def like_post(request, pk):
    user = request.user
    if (not user.is_authenticated):
        return JsonResponse({'error': 'You must login to like posts.'}, status=400)

    post = Post.objects.get(pk=pk)

    if request.method == 'PUT':
        if user in post.likers.all():
            post.likers.remove(user)
            return JsonResponse({'like': False, 'post': post.serialize()}, status=200)
        else:
            post.likers.add(user)
            return JsonResponse({'like': True, 'post': post.serialize()}, status=200)
    return JsonResponse({'error': 'Invalid request type.'}, status=400)

@csrf_exempt
def follow_profile(request, pk):
    user = request.user
    if (not user.is_authenticated):
        return JsonResponse({'error': 'You must login to follow profiles.'}, status=400)

    profile_to_follow = Profile.objects.get(pk=pk)

    if request.method == 'PUT':
        if user.profile == profile_to_follow:
            return JsonResponse({'error': 'Invalid request. You cannot follow yourself.'}, status=400)

        if not profile_to_follow in user.following_profiles.all():
            profile_to_follow.followers.add(user)
            return JsonResponse({'profile': profile_to_follow.serialize()}, status=200)

        else:
            profile_to_follow.followers.remove(user)
            return JsonResponse({'profile': profile_to_follow.serialize()}, status=200)

    return JsonResponse({'error': 'Invalid request type.'}, status=400)

@login_required(login_url = 'login')
def update_profile(request):
    user = request.user
    profile = user.profile
    
    user_form = UserUpdateForm(request.POST or None, instance=user)
    profile_form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    if user_form.is_valid() and profile_form.is_valid():
        profile_form.save()
        user_form.save()

        return HttpResponseRedirect(reverse('user-profile', kwargs={'pk': user.id}))
    
    context['user_form_error'] = user_form.errors
    context['profile_form_error'] = profile_form.errors

    return render(request, 'network/update_profile.html', context)
