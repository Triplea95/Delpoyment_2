from venv import create
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)
    slug = models.SlugField()

    def get_absolute_url(self):
        return reverse("detail", args=[str(self.slug)])

    def __str__(self):
        return self.title



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
