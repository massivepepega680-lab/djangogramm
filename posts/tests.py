import io
import json
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.urls import reverse
from PIL import Image as PilImage
from .models import Image, Like, Post, Tag


@pytest.mark.django_db
class TestPostModels:
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

@pytest.mark.django_db
class TestPostCreationDeletion:
    def test_create_post_view(self, authenticated_client, user1):
        """Tests the full flow of creating a new post, including images, tags,
        tag string representation, and reverse relationships
        """
        url = reverse("posts:create_post")
        image_files = []
        for i in range(2):
            buffer = io.BytesIO()
            PilImage.new("RGB", (100, 100)).save(buffer, format="JPEG")
            buffer.seek(0)
            image_files.append(SimpleUploadedFile(f"test{i}.jpg", buffer.read(), "image/jpeg"))

        post_data = {
            "caption": "A brand new post from a test.",
            "tags": "django, testing, pytest",
            "images": image_files,
        }

        response = authenticated_client.post(url, post_data, follow=True)
        assert response.status_code == 200
        assert Post.objects.count() == 1
        new_post = Post.objects.first()
        assert new_post.author == user1
        assert new_post.caption == "A brand new post from a test."
        assert new_post.images.count() == 2
        assert new_post.tags.count() == 3
        assert "Your new post has been created!" in str(response.content)
        tag_from_db = Tag.objects.get(name="django")
        assert tag_from_db is not None
        assert str(tag_from_db) == "django"
        assert new_post in tag_from_db.posts.all()

    def test_post_delete_view_permissions(self, client, user1, user2, post):
        """Tests that only the author can delete their post"""
        url = reverse("posts:post_delete", kwargs={"post_id": post.id})
        response = client.post(url)
        assert response.status_code == 302
        client.login(username="user2", password="password123")
        response = client.post(url)
        assert response.status_code == 403
        assert Post.objects.filter(id=post.id).exists()

    def test_post_delete_view_success(self, authenticated_client, post):
        """Tests that the author can successfully delete their post"""
        assert Post.objects.count() == 1
        url = reverse("posts:post_delete", kwargs={"post_id": post.id})
        response_get = authenticated_client.get(url)
        assert response_get.status_code == 200
        assert "Are you sure you want to delete this post?" in str(response_get.content)
        response_post = authenticated_client.post(url, follow=True)
        assert response_post.status_code == 200
        assert not Post.objects.filter(id=post.id).exists()
        assert Post.objects.count() == 0
        assert "Your post has been deleted successfully." in str(response_post.content)

@pytest.mark.django_db
class TestApiEndpoints:
    def test_toggle_like_api(self, authenticated_client, user1, post):
        """Tests the AJAX endpoint for liking/unliking, and ensures
        the unique constraint on the Like model is enforced
        """
        url = reverse("posts:toggle_like", kwargs={"post_id": post.id})
        ajax_headers = {"HTTP_ACCEPT": "application/json"}
        response_like = authenticated_client.post(url, **ajax_headers)
        assert response_like.status_code == 200
        data_like = json.loads(response_like.content)
        assert data_like["is_liked"] is True
        assert data_like["like_count"] == 1
        assert post.likers.count() == 1
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Like.objects.create(user=user1, post=post)
        assert post.likers.count() == 1

        response_unlike = authenticated_client.post(url, **ajax_headers)
        assert response_unlike.status_code == 200
        data_unlike = json.loads(response_unlike.content)
        assert data_unlike["is_liked"] is False
        assert data_unlike["like_count"] == 0
        assert post.likers.count() == 0