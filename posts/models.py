from django.conf import settings
from django.db import models
from PIL import Image as PilImage


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    caption = models.TextField(max_length=300, blank=True, default="")
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Like",
        related_name="liked_posts"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post {self.id} by {self.author.username}"

class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="post_images/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("post", "order")
        ordering = ["order"]

    def __str__(self):
        return f"Image for Post {self.post.id} (order: {self.order})"

    def save(self, *args, **kwargs):
        """Overrides the default save method to add image resizing logic"""
        super().save(*args, **kwargs)
        if self.image:
            img = PilImage.open(self.image.path)
            max_width, max_height = (800, 800)
            if img.height > max_height or img.width > max_width:
                img.thumbnail((max_width, max_height))
                img.save(self.image.path)

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.username} liked Post {self.post.id}"