from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from posts.models import Like, Post
from users.models import UserFollowing
from .models import Activity


@login_required
def feed_view(request):
    following_ids = request.user.following.values_list("id", flat=True)

    activities_qs = Activity.objects.filter(
        user_id__in=following_ids
    ).select_related("user")

    activities_list = list(activities_qs)  # Convert to list just before manual prefetching
    generic_relations = {}
    for activity in activities_list:
        model_name = activity.content_type.model
        if model_name not in generic_relations:
            generic_relations[model_name] = []
        generic_relations[model_name].append(activity.object_id)

    if "like" in generic_relations:
        likes = Like.objects.filter(id__in=generic_relations["like"]).select_related("post__author")
        generic_relations["like"] = {like.id: like for like in likes}
    if "post" in generic_relations:
        posts = Post.objects.filter(id__in=generic_relations["post"]).prefetch_related("images")
        generic_relations["post"] = {post.id: post for post in posts}
    if "userfollowing" in generic_relations:
        follows = UserFollowing.objects.filter(id__in=generic_relations["userfollowing"]).select_related(
            "following_user")
        generic_relations["userfollowing"] = {follow.id: follow for follow in follows}

    for activity in activities_list:
        model_name = activity.content_type.model
        object_id = activity.object_id
        if model_name in generic_relations and object_id in generic_relations[model_name]:
            activity.content_object = generic_relations[model_name][object_id]

    context = {
        "activities": activities_list
    }
    return render(request, "activities/feed.html", context)