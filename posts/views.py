from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ImageUploadForm, PostCreateForm
from .models import Image, Like, Post, Tag


def home_view(request):
    posts = Post.objects.all().order_by("-created_at")
    context = {
        "posts": posts
    }
    return render(request, "posts/home.html", context)

@login_required
def toggle_like_view(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if not created:
            like.delete()
            is_liked = False
        else:
            is_liked = True

        return JsonResponse({
            "is_liked": is_liked,
            "like_count": post.likers.count()
        })
    return JsonResponse({"error": "Invalid request method"}, status=400)

@login_required
def create_post_view(request):
    """Handles the logic for creating a new post with multiple images and tags"""
    if request.method == "POST":
        post_form = PostCreateForm(request.POST)
        image_form = ImageUploadForm(request.POST, request.FILES)

        if all([post_form.is_valid(), image_form.is_valid()]):
            post = post_form.save(commit=False)
            post.author = request.user
            post.save()
            tag_string = post_form.cleaned_data.get("tags", "")

            if tag_string:
                tag_names = [name.strip() for name in tag_string.split(",")]
                for name in tag_names:
                    if name:
                        tag, created = Tag.objects.get_or_create(name=name.lower())
                        post.tags.add(tag)

            for i, file in enumerate(image_form.cleaned_data["images"]):
                Image.objects.create(post=post, image=file, order=i)

            messages.success(request, "Your new post has been created!")
            return redirect("posts:post_details", post_id=post.id)
    else:
        post_form = PostCreateForm()
        image_form = ImageUploadForm()

    context = {
        "post_form": post_form,
        "image_form": image_form,
    }
    return render(request, "posts/create_post.html", context)

@login_required
def post_delete_view(request, post_id):
    """Handles the logic for deleting a post"""
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        return HttpResponseForbidden("You are not allowed to delete this post.")

    if request.method == "POST":
        author_username = post.author.username
        post.delete()
        messages.success(request, "Your post has been deleted successfully.")
        return redirect("users:profile", username=author_username)

    context = {
        "post": post
    }
    return render(request, "posts/post_delete_confirm.html", context)

@login_required
def post_details_view(request, post_id):
    """Displays a single post in detail, including all its images,
    tags, caption, creation date, author, like button and delete
    button if you're the post's author
    """
    post = get_object_or_404(Post, pk=post_id)

    is_liked_by_user = False
    if request.user.is_authenticated:
        is_liked_by_user = post.likers.filter(pk=request.user.pk).exists()

    context = {
        "post": post,
        "is_liked_by_user": is_liked_by_user,
    }
    return render(request, "posts/post_details.html", context)