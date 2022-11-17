from django.urls import path
from . import views

app_name = "posts"

urlpatterns = [
    path("", views.index, name="index"),
    path("divide/", views.divide, name="divide"),
    path("scroll/<str:tag_name>", views.scroll, name="scroll"),
    path("create/", views.create, name="create"),
    path("<int:post_pk>/", views.detail, name="detail"),
    path("<int:post_pk>/update", views.update, name="update"),
    path("<int:post_pk>/delete", views.delete, name="delete"),
    path("<int:post_pk>/comments/", views.comments_create, name="comments_create"),
    path(
        "<int:post_pk>/comments/<int:comment_pk>/delete/",
        views.comments_delete,
        name="comments_delete",
    ),
    path("<int:post_pk>/like/", views.like, name="like"),
    path(
        "<int:post_pk>/recomments/<int:comment_pk>",
        views.recomments_create,
        name="recomments_create",
    ),
    path(
        "<int:post_pk>/recomments/<int:recomment_pk>/delete",
        views.recomments_delete,
        name="recomments_delete",
    ),
    path(
        "<int:post_pk>/comments/<int:comment_pk>/update/",
        views.comments_update,
        name="comments_update",
    ),
    path(
        "<int:post_pk>/recomments/<int:comment_pk>/<int:recomment_pk>/update",
        views.recomments_update,
        name="recomments_update",
    ),
    path('search',views.search,name='search'),
]
