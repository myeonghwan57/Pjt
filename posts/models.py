from django.db import models
from django.contrib.auth.models import AbstractUser
from imagekit.models import ProcessedImageField
from imagekit.processors import Thumbnail, ResizeToFill
from django.conf import settings

# Create your models here.
class Post(models.Model):
    tag_choices=(
        ('전체','전체'),
        ('커리어','커리어'),
        ('이직','이직'),
        ('회사생활','회사생활'),
        ('일상','일상'),
        ('개발','개발'),
        ('마케팅','마케팅'),
        ('질문','질문'),
        ('HR','HR'),
        ('기타','기타'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=""
    )
    title = models.CharField(max_length=50)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    like = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="like_posts")
    hits = models.PositiveBigIntegerField(default=1, verbose_name="조회수")
    tag = models.CharField(max_length=50, choices=tag_choices)


class Comment(models.Model):
    content = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    article = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE,  related_name='recomment', null=True)

# # 이미지 업로드 경로 # 다중 이미지 기능 구현시 주석 해제
# def image_upload_path(instance, filename):
#     return f'{instance.post.id}/{filename}'

# class PostImage(models.Model):
#     id = models.AutoField(primary_key=True)
#     post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='image')
#     image = models.ImageField(upload_to=image_upload_path)

#     def __int__(self):
#         return self.id

#     class Meta:
#         db_table = 'post_image'

class Photo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)