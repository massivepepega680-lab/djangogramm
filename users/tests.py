import pytest
from .models import User


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