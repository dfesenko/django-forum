from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .tasks import send_verification_email


# send verification email when new user is registered
@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, *args, **kwargs):
    if created:
        # Send verification email
        send_verification_email.delay(instance.pk)
