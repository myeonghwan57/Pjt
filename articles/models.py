from django.db import models
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone

# Create your models here.


class JobData(models.Model):
    job_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    pseudo_position = models.CharField(max_length=100)
    company_job = models.TextField()
    bookmark = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="bookmark")


class CommentCompany(models.Model):
    content = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    jobs = models.ForeignKey(JobData, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self",
        related_name="reply_set",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    @property
    def created_string(self):
        time = datetime.now(tz=timezone.utc) - self.created_at

        if time < timedelta(minutes=1):
            return "방금 전"
        elif time < timedelta(hours=1):
            return str(int(time.seconds / 60)) + "분 전"
        elif time < timedelta(days=1):
            return str(int(time.seconds / 3600)) + "시간 전"
        elif time < timedelta(days=7):
            time = datetime.now(tz=timezone.utc).date() - self.created_at.date()
            return str(time.days) + "일 전"
        else:
            return False
