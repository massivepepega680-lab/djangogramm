from django.db import models
from django.contrib.auth.models import AbstractUser


class UserFollowing(models.Model):
    user = models.ForeignKey("User", related_name="rel_from_set", on_delete=models.CASCADE)
    following_user = models.ForeignKey("User", related_name="rel_to_set", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "following_user"], name="unique_followers")
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} follows {self.following_user.username}"

class User(AbstractUser):
    full_name = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True, default="")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    following = models.ManyToManyField(
        "self",
        through=UserFollowing,
        related_name="followers",
        symmetrical=False
    )

    def __str__(self):
        return self.username