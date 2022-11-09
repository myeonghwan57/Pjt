from django.db import models
from django.contrib.auth.models import AbstractUser
from imagekit.models import ProcessedImageField
from imagekit.processors import Thumbnail

# Create your models here.
class User(AbstractUser):

    follow = models.ManyToManyField("self", symmetrical=False, related_name="followers")
    profile = ProcessedImageField(
        upload_to="images/profile",
        blank=True,
        processors=[Thumbnail(100, 100)],
        format="JPEG",
        options={"quality": 95},
    )

    @property
    def full_name(self):
        return f"{self.last_name}{self.first_name}"
