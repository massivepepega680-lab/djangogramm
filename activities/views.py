from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Activity
from users.models import UserFollowing


@login_required
def feed_view(request):
    following_ids = UserFollowing.objects.filter(user=request.user).values_list("following_user_id", flat=True)
    user_and_following_ids = list(following_ids) + [request.user.id]
    activities = Activity.objects.filter(user_id__in=user_and_following_ids).select_related(
        "user", "content_type"
    ).prefetch_related("content_object")
    context = {
        "activities": activities
    }
    return render(request, "activities/feed.html", context)