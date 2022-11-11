from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.forms import TextInput
from django import forms


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "password1",
            "password2",
            "career",
        )
        labels = {
            "career": "경력(년차)",
        }
        help_texts = {
            "career": "신입일 경우 0을 입력해주세요.",
        }


class CustomUserChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "profile",
            "career",
            "email",
        )
        labels = {
            "profile": "프로필 사진",
            "career": "경력(년차)",
        }
