from django.shortcuts import render, redirect, get_object_or_404
from .forms import (
    CustomUserCreationForm,
    CustomUserChangeForm,
    CheckPasswordForm,
    NoteForm,
)
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import get_user_model, get_user, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import os, requests
from django.core.files.base import ContentFile
from . import forms, models
from .exception import GithubException, SocialLoginException, OverlapException
from dotenv import load_dotenv
from django.urls import reverse
from posts.models import Post, Comment
from .models import User, Note
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import Count
from django.http import HttpResponseForbidden

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

    # 페이지네이션
    posts = user.post_set.all()
    posts_paginator = Paginator(posts, 6)
    posts_page = request.GET.get("page")
    posts_ls = posts_paginator.get_page(posts_page)

    comments = user.comment_set.all()
    comments_paginator = Paginator(comments, 6)
    comments_page = request.GET.get("page")
    comments_ls = comments_paginator.get_page(comments_page)

    # 커리어 개월수 계산
    now = timezone.now()
    delta = relativedelta(now, user.career)

    # user.post 태그 빈도수 높은 순 세개 호출
    tag_freq = posts.values("tag").annotate(cnt=Count("tag")).order_by("-cnt")[:3]

    # like_posts
    like_posts = user.like_posts.all()
    like_posts_paginator = Paginator(like_posts, 6)
    like_posts_page = request.GET.get("page")
    like_posts_ls = like_posts_paginator.get_page(like_posts_page)
    # bookmarked article
    bookmarked_articles = user.bookmark.all()

    context = {
        "user": user,
        "posts": posts_ls,
        "comments": comments_ls,
        "delta": delta,
        "tagfreq": tag_freq,
        "like_posts_ls": like_posts,
        "like_posts": like_posts_ls,
        "bookmark_articles": bookmarked_articles,
    }
    return render(request, "accounts/detail.html", context)


def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect(request.GET.get("next") or "articles:index")
    else:
        form = AuthenticationForm()
    context = {
        "form": form,
    }
    return render(request, "accounts/login.html", context)


@login_required
def logout(request):
    auth_logout(request)
    messages.warning(request, "이용해주셔서 감사합니다! 다음에 또 방문해주세요.😊")
    return redirect("articles:index")


@login_required
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


@login_required
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


@login_required
def delete_checker(request, pk):
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


@login_required
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


from django.http import JsonResponse


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
        is_followed = False
    else:
        # 팔로우 상태가 아니면, '팔로우'를 누르면 추가 (add)
        user.followers.add(request.user)
        is_followed = True

    data = {
        "is_followed": is_followed,
        "followings_count": user.followers.count(),
        "followers_count": user.follow.count(),
    }
    return JsonResponse(data)


def note(request):

    notes = Note.objects.filter(receive_user=request.user).order_by("-pk")

    context = {"notes": notes}

    return render(request, "accounts/note.html", context)


def send_note(request):

    notes = Note.objects.filter(send_user=request.user).order_by("-pk")

    context = {"notes": notes}

    return render(request, "accounts/sendnote.html", context)


@login_required
def create_note(request):
    user_list = []
    for i in User.objects.all():
        user_list.append(i.username)
    if request.method == "POST":
        note_form = NoteForm(request.POST)
        if request.POST.get("receive_user") not in user_list:
            messages.warning(request, "없는 유저입니다.")
            return redirect("accounts:create_note")
        if request.POST.get("receive_user") == request.user.username:
            messages.warning(request, "자기 자신에게 보낼 수 없습니다.")
            return redirect("accounts:create_note")
        if note_form.is_valid():
            note = note_form.save(commit=False)
            note.send_user = request.user
            note.save()
            return redirect("accounts:note")

    else:
        note_form = NoteForm()

    context = {
        "note_form": note_form,
    }

    return render(request, "accounts/createnote.html", context)


@login_required
def detail_note(request, note_pk):
    note = Note.objects.get(pk=note_pk)
    if (request.user == note.send_user) or (request.user.username == note.receive_user):
        context = {
            "note": note,
        }
        return render(request, "accounts/detailnote.html", context)

    else:
        return HttpResponseForbidden()


@login_required
def delete_note(request, note_pk):
    note = Note.objects.get(pk=note_pk)

    if (request.user == note.send_user) or (request.user.username == note.receive_user):

        if request.user == note.send_user:
            if request.method == "POST":
                note.send_view = True
                note.save()
                return redirect("accounts:send_note")

        if request.user.username == note.receive_user:
            if request.method == "POST":
                note.receive_view = True
                note.save()
                return redirect("accounts:note")

        return redirect("accounts:note")

    else:
        return HttpResponseForbidden()


def follow_page(request, pk):
    user = get_object_or_404(get_user_model(), pk=pk)
    # follow = follow && followers = following
    followings = user.follow.all()
    followers = user.followers.all()
    context = {
        "followings": followings,
        "followers": followers,
    }
    return render(request, "accounts/follow.html", context)
