from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model


class CustumUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("username",)


class CustumUserChangoForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name", "profile")
