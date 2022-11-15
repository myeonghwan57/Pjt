from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.hashers import check_password


class DateInput(forms.DateInput):
    input_type = "date"


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
        # help_texts = {
        #     "career": "신입일 경우 0을 입력해주세요.",
        # }
        widgets = {"career": DateInput()}


class CustomUserChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = get_user_model()
        fields = ("username", "profile", "career", "email", "githuburl")
        labels = {
            "profile": "프로필 사진",
            "career": "경력(년차)",
            "githuburl": "Github 주소",
        }


class CheckPasswordForm(forms.Form):
    password = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = self.user.password

        if password:
            if not check_password(password, confirm_password):
                self.add_error("password", "비밀번호가 일치하지 않습니다.")
