from django.db.models.signals import post_save
from django.dispatch import receiver
from activities.models import Activity
from .models import UserFollowing


@receiver(post_save, sender=UserFollowing)
def create_follow_activity(sender, instance, created, **kwargs):
    if created:
        Activity.objects.create(
            user=instance.user,
            activity_type=Activity.ActivityType.NEW_FOLLOW,
            content_object=instance
        )