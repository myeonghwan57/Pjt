from django.db import models
from django.contrib.auth.models import AbstractUser
from imagekit.models import ProcessedImageField
from imagekit.processors import Thumbnail
from django.conf import settings
import datetime

# Create your models here.
class User(AbstractUser):

    follow = models.ManyToManyField("self", symmetrical=False, related_name="followers")
    profile = ProcessedImageField(
        upload_to="static/images/profile",
        blank=True,
        processors=[Thumbnail(100, 100)],
        format="JPEG",
        options={"quality": 95},
    )
    career = models.DateField(default=datetime.date.today)

    LOGIN_EMAIL = "email"
    LOGIN_GITHUB = "github"
    LOGIN_GOOGLE = "Google"

    LOGIN_CHOICES = (
        (LOGIN_EMAIL, "Email"),
        (LOGIN_GITHUB, "Github"),
        (LOGIN_GOOGLE, "Google"),
    )

    login_method = models.CharField(
        max_length=6, choices=LOGIN_CHOICES, default=LOGIN_EMAIL
    )

    @property
    def full_name(self):
        return f"{self.last_name}{self.first_name}"

    githuburl = models.URLField(max_length=200, blank=True)


class Note(models.Model):

    send_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        default="",
        related_name="send_user",
    )
    receive_user = models.CharField(max_length=50, blank=True)

    title = models.CharField(max_length=50)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    receive_view = models.BooleanField(default=False)
    send_view = models.BooleanField(default=False)
