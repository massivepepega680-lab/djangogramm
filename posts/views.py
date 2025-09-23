from django.http import HttpResponse
from django.shortcuts import render
from .models import Post


def home_view(request):
    posts = Post.objects.all().order_by("-created_at")
    context = {
        "posts": posts
    }
    return render(request, "posts/home.html", context)

def create_post_view(request):
    return HttpResponse("This is the page to create a new post.")

def post_details_view(request, post_id):
    return HttpResponse(f"This is the detail view for post #{post_id}.")