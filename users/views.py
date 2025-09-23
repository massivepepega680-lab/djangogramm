from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import User, UserFollowing


def register_view(request):
    return HttpResponse("This is the placeholder registration page.")

def login_view(request):
    return HttpResponse("This is the placeholder login page.")

@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_following = UserFollowing.objects.filter(user=request.user, following_user=profile_user).exists()
    context = {
        "profile_user": profile_user,
        "is_following": is_following,
    }
    return render(request, "users/profile.html", context)

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow != request.user:
        UserFollowing.objects.get_or_create(user=request.user, following_user=user_to_follow)
    return redirect("users:profile", username=username)

@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    UserFollowing.objects.filter(user=request.user, following_user=user_to_unfollow).delete()
    return redirect("users:profile", username=username)