from django.shortcuts import render, redirect
from .forms import CustumUserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import get_user_model, get_user
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

# Create your views here.


def index(request):
    return render(request, "accounts/index.html")


def signup(request):
    if request.method == "POST":
        form = CustumUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("articles:index")
    else:
        form = CustumUserCreationForm()
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
    else:
        messages.warning(request, "삭제는 본인만 가능합니다.")
    return redirect("accounts:index")
