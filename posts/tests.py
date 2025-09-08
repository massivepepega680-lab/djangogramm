import io
import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from PIL import Image as PilImage
from .models import Image, Like, Post, Tag


User = get_user_model()

@pytest.fixture
def test_user(db):
    """A fixture to create a user for tests"""
    return User.objects.create_user(username='testuser', password='password')

@pytest.fixture
def test_post(test_user):
    """A fixture to create a post"""
    return Post.objects.create(author=test_user, caption="A test caption.")

@pytest.mark.django_db
class TestPostModels:
    def test_post_creation(self, test_user):
        """Tests creating a Post and its relationship to the author"""
        post = Post.objects.create(author=test_user, caption="This is a test.")
        assert Post.objects.count() == 1
        assert post.author == test_user
        assert str(post) == f"Post {post.id} by {test_user.username}"

    def test_like_logic(self, test_user, test_post):
        """
        Tests the business logic of the Like model:
        1. A user can like a post.
        2. A user CANNOT like the same post twice.
        """
        Like.objects.create(user=test_user, post=test_post)
        assert test_post.likes.count() == 1
        assert Like.objects.count() == 1
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Like.objects.create(user=test_user, post=test_post)
        assert test_post.likes.count() == 1

    def test_image_resizing_on_save(self, test_post):
        """
        Tests that the Image model's custom save() method correctly resizes
        a large uploaded image.
        """
        large_image_buffer = io.BytesIO()
        large_image = PilImage.new("RGB", (1200, 1000), "white")
        large_image.save(large_image_buffer, format="JPEG")
        large_image_buffer.seek(0)
        image_file = SimpleUploadedFile(
            name="large_test_image.jpg",
            content=large_image_buffer.read(),
            content_type="image/jpeg"
        )
        image_instance = Image.objects.create(post=test_post, image=image_file)
        saved_image_path = image_instance.image.path
        with PilImage.open(saved_image_path) as resized_img:
            width, height = resized_img.size
        assert width <= 800
        assert height <= 800

    def test_tag_creation(self):
        """Tests that a Tag can be created and its __str__ method works"""
        tag = Tag.objects.create(name="test")
        assert Tag.objects.count() == 1
        assert tag.name == "test"
        assert str(tag) == "test"

    def test_post_and_tag_relationship(self, test_post):
        """Tests the ManyToManyField relationship between Post and Tag"""
        tag1 = Tag.objects.create(name="test1")
        tag2 = Tag.objects.create(name="test2")
        test_post.tags.add(tag1, tag2)
        assert test_post.tags.count() == 2
        assert tag1.posts.count() == 1
        assert tag1.posts.first() == test_post