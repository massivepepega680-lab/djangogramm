import io
import json
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.urls import reverse
from PIL import Image as PilImage
from .models import User, UserFollowing


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
    assert user.get_full_name() == ""
    assert user.bio == ""
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

@pytest.mark.django_db
class TestUserViews:
    def test_profile_view_redirects_guest(self, client):
        """Tests guests being redirected from profile pages"""
        url = reverse("users:profile", kwargs={"username": "anyuser"})
        response = client.get(url)
        assert response.status_code == 302
        assert "/login/" in response.url

@pytest.mark.django_db
def test_user_get_full_name(user1):
    """Tests the get_full_name method on the User model"""
    user1.first_name = "Test"
    user1.last_name = "User"
    user1.save()
    assert user1.get_full_name() == "Test User"
    user1.last_name = ""
    user1.save()
    assert user1.get_full_name() == "Test"

@pytest.mark.django_db
class TestProfileEditing:
    def test_profile_edit_view_get(self, authenticated_client, user1):
        """Tests that the profile edit page loads correctly for the owner"""
        url = reverse("users:profile_edit")
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert user1.bio in str(response.content)

    def test_profile_edit_view_post(self, authenticated_client, user1):
        """Tests updating a user's bio and avatar"""
        url = reverse("users:profile_edit")
        avatar_buffer = io.BytesIO()
        PilImage.new("RGB", (100, 100)).save(avatar_buffer, format="JPEG")
        avatar_buffer.seek(0)
        avatar_file = SimpleUploadedFile("test_avatar.jpg", avatar_buffer.read(), content_type="image/jpeg")
        new_bio = "This is my new, updated bio."

        data = {
            "bio": new_bio,
            "avatar": avatar_file,
        }

        response = authenticated_client.post(url, data, follow=True)
        assert response.status_code == 200
        user1.refresh_from_db()
        assert user1.bio == new_bio
        assert user1.avatar is not None
        assert user1.avatar.name.startswith("avatars/test_avatar")
        assert "Your profile has been updated successfully!" in str(response.content)

    def test_other_user_cannot_edit_profile(self, client, user1, user2):
        """Tests that a user (user2) can only see their own data on the profile edit page,
        not another user's (user1)
        """
        user1.bio = "This is a secret bio for user1."
        user1.save()
        client.login(username="user2", password="password123")
        url = reverse("users:profile_edit")
        response = client.get(url)
        assert response.status_code == 200
        assert user1.bio not in str(response.content)

@pytest.mark.django_db
class TestApiEndpoints:
    def test_follow_unfollow_api(self, client, user1, user2):
        """Tests the AJAX endpoints for following, unfollowing, and ensures
        the unique constraint on the UserFollowing model is enforced
        """
        client.login(username="user1", password="password123")

        follow_url = reverse("users:follow", kwargs={"username": user2.username})
        unfollow_url = reverse("users:unfollow", kwargs={"username": user2.username})
        ajax_headers = {"HTTP_ACCEPT": "application/json"}

        response_follow = client.post(follow_url, **ajax_headers)
        assert response_follow.status_code == 200
        data_follow = json.loads(response_follow.content)
        assert data_follow["is_following"] is True
        assert data_follow["follower_count"] == 1
        assert user2 in user1.following.all()
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                UserFollowing.objects.create(user=user1, following_user=user2)
        assert user1.following.count() == 1
        assert user2.followers.count() == 1

        response_unfollow = client.post(unfollow_url, **ajax_headers)
        assert response_unfollow.status_code == 200
        data_unfollow = json.loads(response_unfollow.content)
        assert data_unfollow["is_following"] is False
        assert data_unfollow["follower_count"] == 0
        assert user2 not in user1.following.all()

    def test_follow_api_requires_login(self, client, user2):
        """Tests that an anonymous user cannot use the follow API"""
        follow_url = reverse("users:follow", kwargs={"username": user2.username})
        ajax_headers = {"HTTP_ACCEPT": "application/json"}

        response = client.post(follow_url, **ajax_headers)
        assert response.status_code == 302
        assert "login" in response.url