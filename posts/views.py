from django.shortcuts import render, redirect
from .models import Post, Comment, Photo
from .forms import PostForm, CommentForm, ReCommentForm
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import date, datetime, timedelta
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator


# Create your views here.


@login_required
def index(request):
    posts = Post.objects.all()
    instances = Post.objects.all().order_by("-hits")[:3]
    sort = request.GET.get("sort", "")  # url의 쿼리스트링을 가져온다. 없는 경우 공백을 리턴한다
    if sort == "likes":
        posts_sort = posts.annotate(like_count=Count("like")).order_by(
            "-like_count", "-created_at"
        )

    elif sort == "comments":
        posts_sort = posts.annotate(comment_count=Count("comment")).order_by(
            "-comment_count", "-created_at"
        )
    else:
        posts_sort = posts.order_by("-created_at")

    page = request.GET.get('page') #GET 방식으로 정보를 받아오는 데이터
    paginator = Paginator(posts_sort, '3') #Paginator(분할될 객체, 페이지 당 담길 객체수)
    page_obj = paginator.get_page(page)
    return render(
        request,
        "posts/index.html",
        {
            "posts_sort": posts_sort,
            "posts": posts,
            "instances": instances,
            "page_obj":page_obj,
            "sort":sort,
        },
    )

def divide(request):

    tag_name = request.POST.get('tag')

    return redirect("posts:scroll",tag_name)


def scroll(request,tag_name):
    if tag_name == '전체':
        return redirect('posts:index')

    instances = Post.objects.all().order_by("-hits")[:3]
    sort = request.GET.get("sort", "")  # url의 쿼리스트링을 가져온다. 없는 경우 공백을 리턴한다
    posts = Post.objects.filter(tag__contains=tag_name)

    if sort == "likes":
        posts_sort = posts.annotate(like_count=Count("like")).order_by(
            "-like_count", "-created_at"
        )


    elif sort == "comments":
        posts_sort = posts.annotate(comment_count=Count("comment")).order_by(
            "-comment_count", "-created_at"
        )

    else:
        posts_sort = posts.order_by("-created_at")

    page = request.GET.get('page','1') #GET 방식으로 정보를 받아오는 데이터
    paginator = Paginator(posts_sort, '3') #Paginator(분할될 객체, 페이지 당 담길 객체수)
    page_obj = paginator.get_page(page)

    return render(
        request,
        "posts/scroll.html",
        {
            "posts_sort": posts_sort,
            "posts": posts,
            "instances": instances,
            "page_obj":page_obj,
            "tag_name":tag_name,
            "sort":sort,

        },
    )


@login_required
def create(request):
    if request.method == "POST":
        post_form = PostForm(request.POST)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.user = request.user
            post.save()
            for img in request.FILES.getlist("imgs"):
                # Photo 객체를 하나 생성한다.
                photo = Photo()
                # 외래키로 현재 생성한 Post의 기본키를 참조한다.
                photo.post = post
                # imgs로부터 가져온 이미지 파일 하나를 저장한다.
                photo.image = img
                # 데이터베이스에 저장
                photo.save()

            return redirect("posts:index")

    else:
        post_form = PostForm()

    context = {
        "post_form": post_form,
    }

    return render(request, "posts/create.html", context)


@login_required
def detail(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    comment_form = CommentForm()
    recomment_form = ReCommentForm()

    expire_date, now = datetime.now(), datetime.now()
    expire_date += timedelta(days=1)
    expire_date = expire_date.replace(hour=0, minute=0, second=0, microsecond=0)
    expire_date -= now
    max_age = expire_date.total_seconds()
    cookie_value = request.COOKIES.get("hitboard", "_")

    context = {
        "post": post,
        "comment_form": comment_form,
        "comments": post.comment_set.all(),
        "recomment_form": recomment_form,
    }

    response = render(request, "posts/detail.html", context)

    if f"_{post_pk}_" not in cookie_value:
        cookie_value += f"{post_pk}_"
        response.set_cookie(
            "hitboard", value=cookie_value, max_age=max_age, httponly=True
        )
        post.hits += 1
        post.save()

    return response


@login_required
def update(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    photo_list = post.photo_set.all()  # post의 이미지를 photo_list에 받아온다.
    if post.user == request.user:
        if request.method == "POST":
            post_form = PostForm(request.POST, request.FILES, instance=post)
            if post_form.is_valid():
                post = post_form.save(commit=False)
                post.save()

                if request.FILES.getlist("imgs"):  # 만약 이미지를 입력했다면
                    for i in photo_list:  # photo_list를 반복하면서 이미지를 모두 삭제한다.
                        i.delete()
                    # 이미지를 모두 삭제하고 다시 추가함.
                    for img in request.FILES.getlist("imgs"):
                        # Photo 객체를 하나 생성한다.
                        photo = Photo()
                        # 외래키로 현재 생성한 Post의 기본키를 참조한다.
                        photo.post = post
                        # imgs로부터 가져온 이미지 파일 하나를 저장한다.
                        photo.image = img
                        # 데이터베이스에 저장
                        photo.save()
                    return redirect("posts:detail", post.pk)

                else:  # 만약 이미지가 입력되지 않았다면
                    if request.POST.getlist("image-clear"):  # 입력된 이미지를 삭제할건지 체크여부 확인
                        for i in photo_list:
                            i.delete()

                    return redirect("posts:detail", post.pk)

        else:
            post_form = PostForm(instance=post)

        context = {
            "post_form": post_form,
            "photo_list": photo_list,
        }
        return render(request, "posts/update.html", context)

    else:
        return HttpResponseForbidden()


@login_required
def delete(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)

    if post.user == request.user:
        if request.method == "POST":
            post.delete()
            return redirect("posts:index")

    else:
        return HttpResponseForbidden()


@login_required
def comments_create(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    if request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.article = post
            comment.user = request.user
            comment.save()
        return redirect("posts:detail", post.pk)


@login_required
def recomments_create(request, post_pk, comment_pk):
    post = get_object_or_404(Post, pk=post_pk)
    if request.user.is_authenticated:
        recomment_form = ReCommentForm(request.POST)
        if recomment_form.is_valid():
            recomment = recomment_form.save(commit=False)
            recomment.article = post
            recomment.user = request.user
            recomment.parent_comment_id = comment_pk
            recomment.save()

        return redirect("posts:detail", post.pk)


@login_required
def comments_update(request, post_pk, comment_pk):
    post = get_object_or_404(Post, pk=post_pk)
    comment = Comment.objects.get(pk=comment_pk)
    if request.method == "POST":
        comment_form = CommentForm(request.POST, instance=comment)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.article = post
            comment.user = request.user
            comment.save()
        return redirect("posts:detail", post_pk)
    else:
        comment_form = CommentForm(instance=comment)
        return redirect("posts:detail", post_pk)


@login_required
def recomments_update(request, post_pk, comment_pk, recomment_pk):
    post = get_object_or_404(Post, pk=post_pk)
    recomment = Comment.objects.get(pk=recomment_pk)
    if request.method == "POST":
        recomment_form = ReCommentForm(request.POST, instance=recomment)
        if recomment_form.is_valid():
            recomment = recomment_form.save(commit=False)
            recomment.article = post
            recomment.user = request.user
            recomment.parent_comment_id = comment_pk
            recomment.save()
        return redirect("posts:detail", post_pk)
    else:
        recomment_form = ReCommentForm(instance=recomment)
        return redirect("posts:detail", post_pk)


@login_required
def recomments_delete(request, post_pk, recomment_pk):
    recomment = get_object_or_404(Comment, pk=recomment_pk)

    if request.user == recomment.user:
        recomment.delete()
        return redirect("posts:detail", post_pk)
    else:
        return HttpResponseForbidden()


@login_required
def comments_delete(request, post_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)

    if request.user == comment.user:
        comment.delete()
        return redirect("posts:detail", post_pk)
    else:
        return HttpResponseForbidden()


def like(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)

    if post.like.filter(pk=request.user.pk).exists():
        post.like.remove(request.user)
        is_likes = False
    else:
        post.like.add(request.user)
        is_likes = True
    data = {"is_likes": is_likes, "likes_count": post.like.count()}
    return JsonResponse(data)
