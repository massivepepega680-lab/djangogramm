import pytest
from .models import User, UserFollowing
from django.db import transaction, IntegrityError
from django.urls import reverse


@pytest.mark.django_db
def test_user_model_creation():
    """Tests that a User can be created with custom fields and defaults"""
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="a-strong-password"
    )
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.check_password("a-strong-password")
    assert not user.check_password("wrong-password")
    assert user.full_name == ''
    assert user.bio == ''
    assert not user.avatar
    assert str(user) == "testuser"

@pytest.mark.django_db
class TestFollowingModel:
    def test_user_can_follow_another(self, user1, user2):
        """Tests that a user can successfully follow another user"""
        user1.following.add(user2)
        assert user1.following.count() == 1
        assert user1.following.first() == user2
        assert user2.followers.count() == 1
        assert user2.followers.first() == user1

    def test_cannot_follow_twice(self, user1, user2):
        """Tests the unique constraint to prevent duplicate follows"""
        UserFollowing.objects.create(user=user1, following_user=user2)
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                UserFollowing.objects.create(user=user1, following_user=user2)
        assert user1.following.count() == 1

@pytest.mark.django_db
class TestUserViews:
    def test_profile_view_redirects_guest(self, client):
        """Tests guests being redirected from profile pages"""
        url = reverse("users:profile", kwargs={"username": "anyuser"})
        response = client.get(url)
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_follow_unfollow_flow(self, client, user1, user2):
        """Tests the complete follow and unfollow view logic for a logged-in user"""
        client.login(username="user1", password="password123")

        follow_url = reverse("users:follow", kwargs={"username": "user2"})
        client.post(follow_url)
        assert user2 in user1.following.all()

        profile_url = reverse("users:profile", kwargs={"username": "user2"})
        response = client.get(profile_url)
        assert b"Unfollow" in response.content

        unfollow_url = reverse("users:unfollow", kwargs={"username": "user2"})
        client.post(unfollow_url)
        assert user2 not in user1.following.all()

        response = client.get(profile_url)
        assert b"Follow" in response.content