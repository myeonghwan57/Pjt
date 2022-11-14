from django.shortcuts import render,redirect
from .models import Post, Comment, Photo
from .forms import PostForm, CommentForm, ReCommentForm
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import date, datetime, timedelta
from django.db import transaction
from django.db.models import Count

# Create your views here.

@login_required
def index(request):
    posts = Post.objects.all()
    sort = request.GET.get('sort','') #url의 쿼리스트링을 가져온다. 없는 경우 공백을 리턴한다
    if request.method == 'POST':
        posts = Post.objects.filter(tag__contains = request.POST.get('tag'))
        if request.POST.get('tag') == '전체':
            posts = Post.objects.all()

    if sort == 'likes':
        posts_sort = posts.annotate(like_count=Count('like')).order_by('-like_count', '-created_at')
        return render(request, 'posts/index.html', {'posts_sort' : posts_sort, 'posts':posts,})
    elif sort == 'comments':
        posts_sort = posts.annotate(comment_count=Count('comment')).order_by('-comment_count', '-created_at')
        return render(request, 'posts/index.html', {'posts_sort' : posts_sort, 'posts':posts,})
    
    else:
        posts_sort = posts.order_by('-created_at')
        return render(request, 'posts/index.html', {'posts_sort' : posts_sort, 'posts':posts,})

@login_required
def create(request):
    if request.method == "POST":
        post_form = PostForm(request.POST)        
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.user = request.user
            post.save()
            for img in request.FILES.getlist('imgs'):
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
    post = Post.objects.get(pk=post_pk)
    comment_form = CommentForm()
    recomment_form = ReCommentForm()

    expire_date,now = datetime.now(), datetime.now()
    expire_date += timedelta(days=1)
    expire_date = expire_date.replace(hour=0, minute=0, second=0, microsecond=0)
    expire_date -= now
    max_age = expire_date.total_seconds()
    cookie_value = request.COOKIES.get('hitboard','_')


    context = {
        "post": post,
        "comment_form": comment_form,
        "comments": post.comment_set.all(),
        "recomment_form":recomment_form,
    }

    response = render(request, "posts/detail.html", context)

    if f'_{post_pk}_' not in cookie_value:
        cookie_value += f'{post_pk}_'
        response.set_cookie('hitboard', value=cookie_value, max_age=max_age, httponly=True)
        post.hits += 1
        post.save()
    
    return response


@login_required
def update(request, post_pk):
    post = Post.objects.get(pk=post_pk)
    photo_list = post.photo_set.all() # post의 이미지를 photo_list에 받아온다.
    if post.user == request.user:
        if request.method == "POST":
            post_form = PostForm(request.POST, request.FILES, instance=post)
            if post_form.is_valid():
                post = post_form.save(commit=False)
                post.save()

                if request.FILES.getlist('imgs'): # 만약 이미지를 입력했다면
                    for i in photo_list: # photo_list를 반복하면서 이미지를 모두 삭제한다.
                        i.delete()
                    # 이미지를 모두 삭제하고 다시 추가함.
                    for img in request.FILES.getlist('imgs'): 
                        # Photo 객체를 하나 생성한다.
                        photo = Photo()
                        # 외래키로 현재 생성한 Post의 기본키를 참조한다.
                        photo.post = post
                        # imgs로부터 가져온 이미지 파일 하나를 저장한다.
                        photo.image = img
                        # 데이터베이스에 저장
                        photo.save()
                    return redirect("posts:detail", post.pk)

                else: # 만약 이미지가 입력되지 않았다면
                    if request.POST.getlist('image-clear'): # 입력된 이미지를 삭제할건지 체크여부 확인
                        for i in photo_list:
                            i.delete()                        

                    return redirect("posts:detail", post.pk)

        else:
            post_form = PostForm(instance=post)

        context = {
            "post_form": post_form,
            "photo_list":photo_list,
        }
        return render(request, "posts/update.html", context)

    else:
        return HttpResponseForbidden()

@login_required
def delete(request,post_pk):
    post = Post.objects.get(pk=post_pk)

    if post.user == request.user:
        if request.method == 'POST':
            post.delete()
            return redirect("posts:index")

    else:
        return HttpResponseForbidden()


@login_required
def comments_create(request,post_pk):
    post = Post.objects.get(pk=post_pk)
    if request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.article = post
            comment.user = request.user
            comment.save()
        return redirect("posts:detail", post.pk)

@login_required
def recomments_create(request,post_pk,comment_pk):
    post = Post.objects.get(pk=post_pk)
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
def recomments_delete(request, post_pk, recomment_pk):
    recomment = Comment.objects.get(pk=recomment_pk)

    if request.user == recomment.user:
        recomment.delete()
        return redirect("posts:detail", post_pk)
    else:
        return HttpResponseForbidden()
    
@login_required
def comments_delete(request, post_pk, comment_pk):
    comment = Comment.objects.get(pk=comment_pk)

    if request.user == comment.user:
        comment.delete()
        return redirect("posts:detail", post_pk)
    else:
        return HttpResponseForbidden()


def like(request,post_pk):
    post = Post.objects.get(pk=post_pk)

    if post.like.filter(pk=request.user.pk).exists():
        post.like.remove(request.user)
        is_likes = False
    else:
        post.like.add(request.user) 
        is_likes=True   
    data = {'is_likes':is_likes,'likes_count':post.like.count()}
    return JsonResponse(data)
