import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from news.models import Profile

log = logging.getLogger(__name__)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def user_saved(instance, created, **kwargs):
    if created:
        message = f"user {instance.pk} created"
        log.info(message)
        Profile.objects.create(user=instance)
