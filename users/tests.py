import io
import json
from unittest import mock
import pytest
from django.core import mail
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

@pytest.mark.django_db
class TestAuthenticationFlow:
    def test_signup_and_activation_flow(self, client, valid_signup_data):
        """Tests the full user journey: signup, email sending, activation,
        and mandatory profile setup
        """
        signup_url = reverse("users:register")
        response_post = client.post(signup_url, valid_signup_data)

        if "form" in response_post.context and response_post.context["form"].errors:
            pytest.fail(f"Signup form had errors: {response_post.context["form"].errors.as_json()}")

        assert response_post.status_code == 302, "Form was valid but did not redirect."
        assert response_post.url == reverse("users:activation_sent")

        response_get = client.get(response_post.url)
        assert response_get.status_code == 200
        assert "users/activation_sent.html" in (t.name for t in response_get.templates)

        user = User.objects.get(username=valid_signup_data["username"])
        assert not user.is_active

        assert len(mail.outbox) == 1
        activation_email = mail.outbox[0]
        assert "Activate Your DjangoGramm Account" in activation_email.subject

        body = activation_email.body
        activation_url = body.split("http://testserver")[1].strip()

        response_activate = client.get(activation_url, follow=True)
        assert response_activate.status_code == 200
        assert "users/profile_setup.html" in (t.name for t in response_activate.templates)

        user.refresh_from_db()
        assert user.is_active
        assert user.is_verified
        assert "_auth_user_id" in client.session

        profile_setup_url = reverse("users:profile_setup")
        profile_data = {
            "first_name": "New",
            "last_name": "User",
            "bio": "Just signed up!",
        }
        response_setup = client.post(profile_setup_url, profile_data, follow=True)
        assert response_setup.status_code == 200
        assert response_setup.request["PATH_INFO"] == reverse(
            "users:profile",
            kwargs={"username": "newuser"}
        )

        user.refresh_from_db()
        assert user.first_name == "New"

    def test_login_with_username_and_email(self, client, db):
        """Tests that a user can log in with either their username or email"""
        User.objects.create_user(
            username="testlogin",
            email="testlogin@example.com",
            password="password123"
        )
        login_url = reverse("users:login")

        login_data_username = {"username": "testlogin", "password": "password123"}
        response = client.post(login_url, login_data_username, follow=True)
        assert response.status_code == 200
        assert "_auth_user_id" in client.session
        client.logout()

        login_data_email = {"username": "testlogin@example.com", "password": "password123"}
        response = client.post(login_url, login_data_email, follow=True)
        assert response.status_code == 200
        assert "_auth_user_id" in client.session
        client.logout()

        login_data_wrong_pass = {"username": "testlogin", "password": "wrongpassword"}
        response = client.post(reverse("users:login"), login_data_wrong_pass)
        assert response.status_code == 200
        assert "_auth_user_id" not in client.session
        assert "alert-danger" in str(response.content)

@pytest.mark.django_db
class TestGoogleAuth:
    @mock.patch("social_core.backends.base.BaseAuth.request")
    def test_google_login_creates_verified_user(self, mock_request, client):
        """Tests the full Google login pipeline by mocking the low-level request method"""
        mock_request.return_value.json.side_effect = [
            {
                "access_token": "dummy-access-token",
                "token_type": "Bearer",
            },
            {
                "id": "12345",
                "email": "googleuser@example.com",
                "verified_email": True,
                "name": "Google User",
                "given_name": "Google",
                "family_name": "User",
            }
        ]

        session = client.session
        session["google-oauth2_state"] = "a_random_state_string"
        session.save()

        complete_url = reverse("social:complete", args=["google-oauth2"])
        response = client.get(
            f"{complete_url}?code=dummy-code&state=a_random_state_string",
            follow=True
        )

        assert response.status_code == 200
        assert User.objects.filter(email="googleuser@example.com").exists()
        new_user = User.objects.get(email="googleuser@example.com")
        assert new_user.is_active
        assert new_user.is_verified
        assert new_user.first_name == "Google"
        assert int(client.session["_auth_user_id"]) == new_user.id