from django.shortcuts import render,redirect
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.http import HttpResponseForbidden, JsonResponse
# Create your views here.

def index(request):
    posts = Post.objects.all()
    context = {"post": posts}

    return render(request, "posts/index.html", context)

def create(request):
    if request.method == "POST":
        post_form = PostForm(request.POST)
        if post_form.is_valid():
            form = post_form.save(commit=False)
            form.user = request.user
            form.save()
            return redirect("posts:index")

    else:
        post_form = PostForm()

    context = {"post_form": post_form}

    return render(request, "posts/create.html", context)


def detail(request, post_pk):
    post = Post.objects.get(pk=post_pk)
    comment_form = CommentForm()
    
    context = {
        "post": post,
        "comment_form": comment_form,
        "comments": post.comment_set.all(),
    }
    return render(request, "posts/detail.html", context)


def update(request, post_pk):
    post = Post.objects.get(pk=post_pk)
    if post.user == request.user:

        if request.method == "POST":
            post_form = PostForm(request.POST, instance=post)
            if post_form.is_valid():
                form = post_form.save(commit=False)
                form.user = request.user
                form.save()
                return redirect("posts:detail", post.pk)

        else:
            post_form = PostForm(instance=post)

        context = {"post_form": post_form}

        return render(request, "posts/update.html", context)

    else:
        return HttpResponseForbidden()

def delete(request,post_pk):
    post = Post.objects.get(pk=post_pk)

    if post.user == request.user:
        if request.method == 'POST':
            post.delete()
            return redirect("posts:index")

    else:
        return HttpResponseForbidden()

def comments_create(request,post_pk):
    post = Post.objects.get(pk=post_pk)
    if request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
        return redirect("posts:detail", post.pk)
    
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