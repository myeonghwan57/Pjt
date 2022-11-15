from django.shortcuts import render, get_object_or_404
from .models import JobData

# Create your views here.


def index(request):
    Joblists = JobData.objects.order_by("id")
    context = {"Joblists": Joblists}
    return render(request, "articles/index.html", context)


def detail(request, pk):
    jobs = get_object_or_404(JobData, pk=pk)

    context = {
        "jobs": jobs,
    }

    return render(request, "articles/detail.html", context)
