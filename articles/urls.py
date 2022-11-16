from django.urls import path
from . import views

app_name = "articles"

urlpatterns = [
    path("", views.index, name="index"),
    path("details/<int:pk>/", views.detail, name="detail"),
    path(
        "details/<int:jobs_pk>/comments/",
        views.comment_create,
        name="company_comment_create",
    ),
    path(
        "details/<int:jobs_pk>/comments/<int:comment_pk>/delete/",
        views.comment_delete,
        name="company_comment_delete",
    ),
    path(
        "details/<int:jobs_pk>/comments/<int:comment_pk>/reply/",
        views.reply_create,
        name="company_reply_create",
    ),
    path("details/<int:pk>/bookmark/", views.bookmark, name="bookmark"),

]
