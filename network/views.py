import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, resolve_url
from django.urls import reverse
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import User, Post
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

def index(request):
    all_posts = Post.objects.all().order_by("id").reverse()
    paginator = Paginator(all_posts, 10) # Show 10 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "all_posts": all_posts,
        'page_obj': page_obj
    })


@csrf_exempt
@login_required
def like_post(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            post_id = data.get('post_id')
            post = Post.objects.get(id=post_id)
            user = request.user
            
            if user in post.likes.all():
                post.likes.remove(user)
                liked = False
            else:
                post.likes.add(user)
                liked = True

            return JsonResponse({'liked': liked, 'like_count': post.likes.count()})
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
@login_required
def post(request, id):
    if request.method == "PUT":
        post = Post.objects.get(pk=id)
        data = json.loads(request.body)
        post.content = data["content"]
        post.save()
        return JsonResponse({'content': post.content})
    
def following(request):
    following = request.user.following.all()
    all_posts = Post.objects.all().order_by('id').reverse()
    needed_posts = []
    for post in all_posts:
        if post.user in following:
            needed_posts.append(post)
    paginator = Paginator(needed_posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "network/following.html", {
        "page_obj": page_obj
    }) 


def profile(request, username):
    profile = User.objects.get(username=username)
    all_posts = Post.objects.filter(user=profile).order_by('id').reverse()
    following = profile.following.all()
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request,  "network/profile.html", {
        "profile": profile,
        "all_posts": all_posts,
        "page_obj": page_obj,
        "following": following
    })

def follow(request, username):
    profile = User.objects.get(username=username)
    if request.method == 'POST' :
        if profile not in request.user.following.all():
            request.user.following.add(profile)
        else:
            request.user.following.remove(profile)
       
        return HttpResponseRedirect(resolve_url("profile", username=username))

def new_post(request):
    if request.method == 'POST':
        content = request.POST['content']
        user = request.user
        post = Post(content=content, user=user)
        post.save()
    return HttpResponseRedirect(reverse(index))

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
