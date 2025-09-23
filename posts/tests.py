import io
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.urls import reverse
from PIL import Image as PilImage
from .models import Image, Like, Post, Tag


@pytest.mark.django_db
class TestPostModels:
    def test_tag_creation(self):
        """Tests that a Tag can be created and its __str__ method works"""
        tag = Tag.objects.create(name="travel")
        assert Tag.objects.count() == 1
        assert str(tag) == "travel"

    def test_post_and_tag_relationship(self, post):
        """Tests the ManyToManyField relationship between Post and Tag"""
        tag1 = Tag.objects.create(name="photography")
        tag2 = Tag.objects.create(name="testing")
        post.tags.add(tag1, tag2)
        assert post.tags.count() == 2
        assert tag1.posts.first() == post

    def test_post_creation(self, user1):
        """Tests creating a Post and its relationship to the author"""
        post = Post.objects.create(author=user1, caption="This is a test.")
        assert post.author == user1
        assert str(post) == f"Post {post.id} by {user1.username}"

    def test_like_logic(self, user1, user2, post):
        """Tests the business logic of the Like model"""
        post.likers.add(user2)
        assert post.likers.count() == 1
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Like.objects.create(user=user2, post=post)
        assert post.likers.count() == 1

    def test_image_resizing_on_save(self, post):
        """Tests that the Image model's save() method resizes a large image"""
        large_image_buffer = io.BytesIO()
        large_image = PilImage.new("RGB", (1200, 1000), "white")
        large_image.save(large_image_buffer, format="JPEG")
        large_image_buffer.seek(0)
        image_file = SimpleUploadedFile(
            name="large_test_image.jpg",
            content=large_image_buffer.read(),
            content_type="image/jpeg"
        )
        image_instance = Image.objects.create(post=post, image=image_file)
        with PilImage.open(image_instance.image.path) as resized_img:
            width, height = resized_img.size
        assert width <= 800 and height <= 800

@pytest.mark.django_db
class TestHomepageView:
    def test_homepage_loads_for_anonymous_user(self, client):
        """Tests that the homepage is public and loads successfully"""
        url = reverse("home")
        response = client.get(url)
        assert response.status_code == 200

    def test_homepage_shows_posts(self, client, post):
        """Tests that posts appear on the homepage"""
        url = reverse("home")
        response = client.get(url)
        assert response.status_code == 200
        assert post.caption in str(response.content)