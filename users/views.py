from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from .forms import (CustomAuthenticationForm, CustomUserCreationForm,
                    ProfileEditForm, ProfileSetupForm)
from .models import User, UserFollowing
from .tokens import account_activation_token


def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            subject = "Activate Your DjangoGramm Account"
            message = render_to_string("users/activation_email.html", {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            })
            user.email_user(subject, message)

            return redirect("users:activation_sent")
    else:
        form = CustomUserCreationForm()
    return render(request, "users/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("users:profile", username=user.username)
    else:
        form = CustomAuthenticationForm()

    return render(request, "users/login.html", {"form": form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect("home")

def activation_sent_view(request):
    return render(request, "users/activation_sent.html")

def activate_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.is_verified = True
        user.save()
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("users:profile_setup")
    else:
        return HttpResponse("Activation link is invalid!")

@login_required
def profile_setup_view(request):
    if request.method == "POST":
        form = ProfileSetupForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Welcome to DjangoGramm! Your profile is now set up.")
            return redirect("users:profile", username=request.user.username)
    else:
        form = ProfileSetupForm(instance=request.user)

    return render(request, "users/profile_setup.html", {"form": form})

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