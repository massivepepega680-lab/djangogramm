from django.db.models.signals import post_save
from django.dispatch import receiver
from activities.models import Activity
from .models import Post, Like


@receiver(post_save, sender=Post)
def create_post_activity(sender, instance, created, **kwargs):
    if created:
        Activity.objects.create(
            user=instance.author,
            activity_type=Activity.ActivityType.NEW_POST,
            content_object=instance
        )

@receiver(post_save, sender=Like)
def create_like_activity(sender, instance, created, **kwargs):
    if created:
        Activity.objects.create(
            user=instance.user,
            activity_type=Activity.ActivityType.NEW_LIKE,
            content_object=instance
        )