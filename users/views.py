from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ProfileEditForm
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
        request.user.following.add(user_to_follow)

    if "application/json" in request.headers.get("Accept", ""):
        return JsonResponse({
            "is_following": True,
            "follower_count": user_to_follow.followers.count(),
        })

    return redirect("users:profile", username=username)

@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    request.user.following.remove(user_to_unfollow)

    if "application/json" in request.headers.get("Accept", ""):
        return JsonResponse({
            "is_following": False,
            "follower_count": user_to_unfollow.followers.count(),
        })

    return redirect("users:profile", username=username)

@login_required
def profile_edit_view(request):
    """Handles the logic for a user editing their own profile"""
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect("users:profile", username=request.user.username)
    else:
        form = ProfileEditForm(instance=request.user)

    context = {
        "form": form
    }
    return render(request, "users/profile_edit.html", context)