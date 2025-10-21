import pytest
from django.contrib.auth import get_user_model
from posts.models import Post


User = get_user_model()

@pytest.fixture
def user1(db):
    """Fixture to create a primary test user"""
    return User.objects.create_user(username="user1", password="password123")

@pytest.fixture
def user2(db):
    """Fixture to create a secondary test user for interactions"""
    return User.objects.create_user(username="user2", password="password123")

@pytest.fixture
def post(user1):
    """Fixture to create a post, authored by user1"""
    return Post.objects.create(author=user1, caption="A test caption from a fixture.")

@pytest.fixture
def authenticated_client(client, user1):
    """A Django test client logged in as user1"""
    client.login(username="user1", password="password123")
    return client

@pytest.fixture(autouse=True)
def use_tmpdir_for_media(tmpdir, settings):
    """Forces the test runner to use a temporary directory
    for all media file uploads
    """
    settings.MEDIA_ROOT = str(tmpdir)

@pytest.fixture
def valid_signup_data():
    """Provides a dictionary of valid data for the user creation form"""
    return {
        "username": "newuser",
        "email": "newuser@example.com",
        "password1": "a-strong-password123",
        "password2": "a-strong-password123",
    }