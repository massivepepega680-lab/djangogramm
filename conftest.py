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
    """Fixture to create a post, authored by user1."""
    return Post.objects.create(author=user1, caption="A test caption from a fixture.")