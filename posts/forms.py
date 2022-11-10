from django.forms import ModelForm
from .models import Post,Comment

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('title','content','image','tag',)
        labels={
            'title':"글 제목",
            'content':'글 내용',
            'tag':'태그',
        }

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        labels={
            'content':'댓글 내용',
        }