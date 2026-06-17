from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        try:
            if instance.email:
                send_mail(
                    subject='Welcome to MegaMartX!',
                    message=f"Hello {instance.first_name}, welcome to MegaMartX! We're glad to have you here.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.email],
                    fail_silently=True,
                )
        except Exception as e:
            print("Error sending welcome email:", e)
