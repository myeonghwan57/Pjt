from django.shortcuts import render, redirect, get_object_or_404
from .forms import CommentCompanyForm, ReplyCompanyForm
from .models import JobData, CommentCompany
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import timedelta, timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.template.defaultfilters import linebreaksbr

# Create your views here.


def index(request):
    Joblists = JobData.objects.order_by("id")

    for i in range(1, len(Joblists)+1):
        jobs = JobData.objects.get(pk=i)
        job_list = list(jobs.pseudo_position.split(","))
        lst = []
        for i in job_list:
            i = list(i)
            tmp = []
            for j in range(len(i)):
                if str(i[j]) != '"':
                    tmp.append(str(i[j]))
            lst.append("".join(tmp))
        jobs.pseudo_position = ""

        for h in range(len(lst)):
            jobs.pseudo_position += lst[h] + " "

    context = {
        "Joblists": Joblists,
    }
    return render(request, "articles/index.html", context)


def detail(request, pk):
    jobs = get_object_or_404(JobData, pk=pk)
    job_list = list(jobs.pseudo_position.split(","))

    lst = []
    for i in job_list:
        i = list(i)
        tmp = []
        for j in range(len(i)):
            if str(i[j]) != '"':
                tmp.append(str(i[j]))
        lst.append("".join(tmp))
    jobs.pseudo_position = lst
    br = jobs.company_job
    br = str(br).replace('"', "")
    br = list(str(br).split("\\n"))
    jobs.company_job = br
    context = {
        "jobs": jobs,
        "comments": CommentCompany.objects.select_related("user").filter(
            jobs=jobs, parent=None
        ),
        "comments_count": CommentCompany.objects.filter(jobs=jobs).count(),
        "comment_form": CommentCompanyForm(),
        "reply_form": ReplyCompanyForm(),
    }

    return render(request, "articles/detail.html", context)


@require_POST
def comment_create(request, jobs_pk):
    jobs = get_object_or_404(JobData, pk=jobs_pk)

    if request.user.is_authenticated:
        comment_form = CommentCompanyForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.jobs = jobs
            comment.user = request.user
            comment.save()

            queryset = CommentCompany.objects.select_related("user").filter(jobs=jobs)
            queryset_list = list()
            for query in queryset:
                if query.parent == None:
                    queryset_list.append(
                        {
                            "pk": query.pk,
                            "parent": None,
                            "content": query.content,
                            "created_at": query.created_string
                            or query.created_at.astimezone(
                                timezone(timedelta(hours=9))
                            ).strftime("%Y-%m-%d %A"),
                            "username": query.user.username,
                        }
                    )
                else:
                    queryset_list.append(
                        {
                            "pk": query.pk,
                            "parent": query.parent.pk,
                            "content": query.content,
                            "created_at": query.created_string
                            or query.created_at.astimezone(
                                timezone(timedelta(hours=9))
                            ).strftime("%Y-%m-%d %A"),
                            "username": query.user.username,
                        }
                    )

            context = {
                "comments_count": queryset.count(),
                "comments": queryset_list,
                "jobs_pk": jobs.pk,
                "request_is_authenticated": request.user.is_authenticated,
                "request_username": request.user.username,
            }
            print(context["comments"])
            return JsonResponse(context)
        else:
            messages.warning(request, "양식이 유효하지 않습니다.")
            return redirect("articles:detail", jobs.pk)
    else:
        messages.warning(request, "로그인이 필요합니다.")
        return redirect("accounts:login")


@require_POST
def reply_create(request, jobs_pk, comment_pk):
    jobs = get_object_or_404(JobData, pk=jobs_pk)
    parent_comment = get_object_or_404(CommentCompany, pk=comment_pk)

    if request.user.is_authenticated:
        reply_form = ReplyCompanyForm(request.POST)
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.jobs = jobs
            reply.parent = parent_comment
            reply.user = request.user
            reply.save()

            queryset = CommentCompany.objects.select_related("user").filter(jobs=jobs)
            queryset_list = list()
            for query in queryset:
                if query.parent == None:
                    queryset_list.append(
                        {
                            "pk": query.pk,
                            "parent": None,
                            "content": query.content,
                            "created_at": query.created_string
                            or query.created_at.astimezone(
                                timezone(timedelta(hours=9))
                            ).strftime("%Y-%m-%d %A"),
                            "username": query.user.username,
                        }
                    )
                else:
                    queryset_list.append(
                        {
                            "pk": query.pk,
                            "parent": query.parent.pk,
                            "content": query.content,
                            "created_at": query.created_string
                            or query.created_at.astimezone(
                                timezone(timedelta(hours=9))
                            ).strftime("%Y-%m-%d %A"),
                            "username": query.user.username,
                        }
                    )

            context = {
                "comments_count": queryset.count(),
                "comments": queryset_list,
                "jobs_pk": jobs.pk,
                "request_is_authenticated": request.user.is_authenticated,
                "request_username": request.user.username,
            }
            return JsonResponse(context)
        else:
            messages.warning(request, "양식이 유효하지 않습니다.")
            return redirect("articles:detail", jobs.pk)
    else:
        messages.warning(request, "로그인이 필요합니다.")
        return redirect("accounts:login")


@login_required
@require_POST
def comment_delete(request, jobs_pk, comment_pk):
    jobs = get_object_or_404(JobData, pk=jobs_pk)
    comment = get_object_or_404(CommentCompany, pk=comment_pk)

    if request.method == "POST":
        if request.user == comment.user:
            comment.delete()
            queryset = CommentCompany.objects.select_related("user").filter(jobs=jobs)
            queryset_list = list()
            for query in queryset:
                if query.parent == None:
                    queryset_list.append(
                        {
                            "pk": query.pk,
                            "parent": None,
                            "content": query.content,
                            "created_at": query.created_string
                            or query.created_at.astimezone(
                                timezone(timedelta(hours=9))
                            ).strftime("%Y-%m-%d %A"),
                            "username": query.user.username,
                        }
                    )
                else:
                    queryset_list.append(
                        {
                            "pk": query.pk,
                            "parent": query.parent.pk,
                            "content": query.content,
                            "created_at": query.created_string
                            or query.created_at.astimezone(
                                timezone(timedelta(hours=9))
                            ).strftime("%Y-%m-%d %A"),
                            "username": query.user.username,
                        }
                    )

        context = {
            "comments_count": queryset.count(),
            "comments": queryset_list,
            "jobs_pk": jobs.pk,
            "request_is_authenticated": request.user.is_authenticated,
            "request_username": request.user.username,
        }
        return JsonResponse(context)
    else:
        messages.warning(request, "댓글 작성자만 삭제 가능합니다.")
        return redirect("articles:detail", jobs_pk)


@login_required
def bookmark(request, pk):
    jobdata = JobData.objects.get(pk=pk)
    if jobdata.bookmark.filter(pk=request.user.pk).exists():
        jobdata.bookmark.remove(request.user)
        is_bookmarked = False
    else:
        jobdata.bookmark.add(request.user)
        is_bookmarked = True
    data = {
        "is_bookmarked": is_bookmarked,
    }
    return JsonResponse(data)