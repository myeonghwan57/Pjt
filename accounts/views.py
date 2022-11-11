from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomUserChangeForm, CheckPasswordForm
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import get_user_model, get_user, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from posts.models import Post, Comment

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
    user = get_user_model().objects.get(pk=pk)
    if request.method == "POST":
        password_form = CheckPasswordForm("request.user", request.POST)

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


# def delete(request, pk):
#     user = get_user_model().objects.get(pk=pk)
#     if request.user == user:
#         user.delete()
#         auth_logout(request)
#     else:
#         messages.warning(request, "삭제는 본인만 가능합니다.")
#     return redirect("articles:index")
