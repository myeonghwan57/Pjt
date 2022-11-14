from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, CustomUserChangeForm, CheckPasswordForm
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import get_user_model, get_user, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required

import os, requests
from django.core.files.base import ContentFile
from . import forms, models
from .exception import GithubException, SocialLoginException, OverlapException
from dotenv import load_dotenv
from django.urls import reverse
from posts.models import Post, Comment
from .models import User

# Create your views here.
def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(
                request, user, backend="django.contrib.auth.backends.ModelBackend"
            )
            return redirect("articles:index")
    else:
        form = CustomUserCreationForm()
    context = {
        "form": form,
    }
    return render(request, "accounts/signup.html", context)


def detail(request, pk):
    user = get_user_model().objects.get(pk=pk)
    posts = user.post_set.all()
    comments = user.comment_set.all()
    context = {
        "user": user,
        "posts": posts,
        "comments": comments,
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


def delete_checker(request, pk):
    user = request.user
    if request.method == "POST":
        password_form = CheckPasswordForm(request.user, request.POST)

        if password_form.is_valid():
            request.user.delete()
            logout(request)
            messages.success(request, "회원탈퇴완료")
            return redirect("accounts:login")
    else:
        password_form = CheckPasswordForm(request.user)
    context = {
        "password_form": password_form,
    }
    return render(request, "accounts/pw_check.html", context)


def social_delete(request, pk):
    user = get_user_model().objects.get(pk=pk)
    if request.user == user:
        user.delete()
        auth_logout(request)
    else:
        messages.warning(request, "삭제는 본인만 가능합니다.")
    return redirect("articles:index")


def github_login(request):
    load_dotenv()
    try:
        if request.user.is_authenticated:
            raise SocialLoginException("User already logged in")
        client_id = os.environ.get("GITHUB_ID")
        redirect_uri = "http://127.0.0.1:8000/accounts/login/github/callback"
        return redirect(
            f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=read:user"
        )  # 👈 사용자가 승인을 누르면, redirect_uri 경로로 redirect 됩니다.
    except SocialLoginException as error:
        messages.error(request, error)
        return redirect("articles:index")


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
        username = profile_json.get("login", None)

        if username is None:
            raise GithubException("Can't get username from profile_request")

        # name = profile_json.get("name", None)
        # if name is None:
        #     raise GithubException("Can't get name from profile_request")

        # bio = profile_json.get("bio", None)
        # if bio is None:
        #     raise GithubException("Can't get bio from profile_request")

        # overlap = False

        # for i in check_users:
        #     if i.username == username:
        #         overlap = True

        # if overlap == True:
        #     raise OverlapException("가입된 아이디가 있습니다.")

        try:
            user = models.User.objects.get(username=username)

            if user.login_method != models.User.LOGIN_GITHUB:
                raise GithubException(f"Please login with {user.login_method}")
        except models.User.DoesNotExist:
            user = models.User.objects.create(
                username=username,
                login_method=models.User.LOGIN_GITHUB,
                githuburl=f"http://github.com/{username}",
            )

            user.set_unusable_password()
            user.save()
            messages.success(request, f"{user.email} logged in with Github")

        auth_login(request, user, backend="social_core.backends.github.GithubOAuth2")
        return redirect(reverse("articles:index"))
    except GithubException as error:
        messages.error(request, error)
        return redirect(reverse("articles:index"))
    except SocialLoginException as error:
        messages.error(request, error)
        return redirect(reverse("articles:index"))

    except OverlapException as error:
        messages.error(request, error)
        return redirect(reverse("articles:index"))


@login_required
def follow(request, user_pk):
    # 프로필에 해당하는 유저를 로그인한 유저가!
    user = get_object_or_404(get_user_model(), pk=user_pk)
    if request.user == user:
        messages.warning(request, "스스로 팔로우 할 수 없습니다.")
        return redirect("accounts:detail", user_pk)
    if request.user in user.followers.all():
        # (이미) 팔로우 상태이면, '팔로우 취소'버튼을 누르면 삭제 (remove)
        user.followers.remove(request.user)
    else:
        # 팔로우 상태가 아니면, '팔로우'를 누르면 추가 (add)
        user.followers.add(request.user)
    return redirect("accounts:detail", user_pk)
