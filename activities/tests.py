import pytest
from django.urls import reverse
from .models import Activity
from posts.models import Post, Like
from users.models import UserFollowing


@pytest.mark.django_db
class TestActivityCreationSignals:
    def test_post_creation_creates_activity(self, user1):
        """Tests that creating a Post triggers the creation of an Activity"""
        assert Activity.objects.count() == 0
        post = Post.objects.create(author=user1, caption="A new post!")
        assert Activity.objects.count() == 1
        activity = Activity.objects.first()
        assert activity.user == user1
        assert activity.activity_type == Activity.ActivityType.NEW_POST
        assert activity.content_object == post

    def test_like_creation_creates_activity(self, user1, user2):
        """Tests that creating a Like triggers the creation of an Activity"""
        post = Post.objects.create(author=user2, caption="A post to be liked.")
        assert Activity.objects.count() == 1
        like = Like.objects.create(user=user1, post=post)
        assert Activity.objects.count() == 2
        activity = Activity.objects.latest("created_at")
        assert activity.user == user1
        assert activity.activity_type == Activity.ActivityType.NEW_LIKE
        assert activity.content_object == like

    def test_follow_creation_creates_activity(self, user1, user2):
        """Tests that creating a UserFollowing triggers an Activity"""
        assert Activity.objects.count() == 0
        follow = UserFollowing.objects.create(user=user1, following_user=user2)
        assert Activity.objects.count() == 1
        activity = Activity.objects.first()
        assert activity.user == user1
        assert activity.activity_type == Activity.ActivityType.NEW_FOLLOW
        assert activity.content_object == follow

@pytest.mark.django_db
class TestFeedView:
    def test_feed_redirects_anonymous(self, client):
        """Tests personalized feed redirecting guests"""
        url = reverse("activities:feed")
        response = client.get(url)
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_feed_shows_followed_user_content(self, client, user1, user2):
        """Tests feed showing activities from users the logged-in user follows"""
        UserFollowing.objects.create(user=user1, following_user=user2)
        post_by_user2 = Post.objects.create(author=user2, caption="Hello from user2!")
        activity = Activity.objects.get(
            activity_type=Activity.ActivityType.NEW_POST,
            object_id=post_by_user2.id
        )
        assert activity.user == user2
        assert activity.content_object == post_by_user2
        client.login(username="user1", password="password123")
        url = reverse("activities:feed")
        response = client.get(url)
        assert response.status_code == 200
        assert "Hello from user2!" in str(response.content)

    def test_feed_hides_unfollowed_user_content(self, client, user1, user2, db):
        """Tests feed NOT showing activities from users the logged-in user does not follow"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user3 = User.objects.create_user(username="user3", password="password123")
        UserFollowing.objects.create(user=user1, following_user=user2)
        post_by_user3 = Post.objects.create(author=user3, caption="You should not see this.")
        assert Activity.objects.filter(
            activity_type=Activity.ActivityType.NEW_POST,
            object_id=post_by_user3.id
        ).exists()
        client.login(username="user1", password="password123")
        url = reverse("activities:feed")
        response = client.get(url)
        assert response.status_code == 200
        assert "You should not see this." not in str(response.content)