from django import forms
from .models import JobData, CommentCompany


class CommentCompanyForm(forms.ModelForm):
    content = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "댓글을 남겨보세요 💬",
            }
        ),
    )

    class Meta:
        model = CommentCompany
        fields = [
            "content",
        ]


class ReplyCompanyForm(forms.ModelForm):
    content = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "대댓글을 남겨보세요 💬",
            }
        ),
    )

    class Meta:
        model = CommentCompany
        fields = [
            "content",
        ]
