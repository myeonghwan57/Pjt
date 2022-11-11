from django.forms import ModelForm, TextInput
from .models import Post,Comment
from django import forms

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('title','content','tag',)
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

class ReCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        labels = {
            'content': '',
        }
        widgets = {
            'content': TextInput(attrs={
                'placeholder': '답글 내용을 입력해 주세요.',
            })
        }




