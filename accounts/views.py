from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import get_user_model, get_user, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
import os, requests
from django.core.files.base import ContentFile
from . import forms, models
from .exception import GithubException,SocialLoginException
from dotenv import load_dotenv
from django.urls import reverse
# Create your views here.


def index(request):
    return render(request, "accounts/index.html")


def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("articles:index")
    else:
        form = CustomUserCreationForm()
    context = {
        "form": form,
    }
    return render(request, "accounts/signup.html", context)


def detail(request, pk):
    user = get_user_model().objects.get(pk=pk)
    context = {
        "user": user,
    }
    return render(request, "accounts/detail.html", context)


def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            messages.success(request, "로그인 되었습니다.")
            return redirect(request.GET.get("next") or "articles:index")
    else:
        form = AuthenticationForm()
    context = {
        "form": form,
    }
    return render(request, "accounts/login.html", context)


def logout(request):
    auth_logout(request)
    messages.warning(request, "로그아웃")
    return redirect("articles:index")


def delete(request, pk):
    user = get_user_model().objects.get(pk=pk)
    if request.user == user:
        user.delete()
        auth_logout(request)
    else:
        messages.warning(request, "삭제는 본인만 가능합니다.")
    return redirect("accounts:detail", pk)


def update(request):
    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("accounts:detail", request.user.pk)
    else:
        form = CustomUserChangeForm(instance=request.user)
    context = {
        "form": form,
    }
    return render(request, "accounts/signup.html", context)


def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect("articles:index")
    else:
        form = PasswordChangeForm(request.user)
    context = {
        "form": form,
    }
    return render(request, "accounts/passwordchange.html", context)

def github_login(request):
    load_dotenv()
    try:
        if request.user.is_authenticated:
            raise SocialLoginException("User already logged in")
        client_id = os.environ.get("GITHUB_ID")
        redirect_uri = "http://127.0.0.1:8000/accounts/login/github/callback"
        return redirect(    
            f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=read:user"
        ) # 👈 사용자가 승인을 누르면, redirect_uri 경로로 redirect 됩니다.
    except SocialLoginException as error:
        messages.error(request, error)
        return redirect("accounts:index")

def github_login_callback(request):
    load_dotenv()
    try:
        if request.user.is_authenticated:
            raise SocialLoginException("User already logged in")
        print(request.GET)
        code = request.GET.get("code", None)
        if code is None:
            raise GithubException("Can't get code")

        client_id = os.environ.get("GITHUB_ID")
        client_secret = os.environ.get("GITHUB_SECRET")

        token_request = requests.post(
            f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
            headers={"Accept": "application/json"},
        )
        token_json = token_request.json()
        error = token_json.get("error", None)

        if error is not None:
            raise GithubException("Can't get access token")

        access_token = token_json.get("access_token")
        profile_request = requests.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/json",
            },
        )
        profile_json = profile_request.json()
        print(profile_json)
        username = profile_json.get("login", None)

        if username is None:
            raise GithubException("Can't get username from profile_request")

        # name = profile_json.get("name", None)
        # if name is None:
        #     raise GithubException("Can't get name from profile_request")

        email = profile_json.get("email", None)
        if email is None:
            raise GithubException("Can't get email from profile_request")

        # bio = profile_json.get("bio", None)
        # if bio is None:
        #     raise GithubException("Can't get bio from profile_request")

        try:
            user = models.User.objects.get(email=email)

            if user.login_method != models.User.LOGIN_GITHUB:
                raise GithubException(f"Please login with {user.login_method}")
        except models.User.DoesNotExist:
            user = models.User.objects.create(
                username=email,
                email=email,
                login_method=models.User.LOGIN_GITHUB,
            )

            user.set_unusable_password()
            user.save()
            messages.success(request, f"{user.email} logged in with Github")
        auth_login(request, user, backend='social_core.backends.github.GithubOAuth2')
        return redirect(reverse("accounts:index"))
    except GithubException as error:
        messages.error(request, error)
        return redirect(reverse("accounts:index"))
    except SocialLoginException as error:
        messages.error(request, error)
        return redirect(reverse("accounts:index"))