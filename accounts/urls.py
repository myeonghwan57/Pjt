from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("<int:pk>/", views.detail, name="detail"),
    path("update/", views.update, name="update"),
    path("note/", views.note, name="note"),
    path("sendnote/", views.send_note, name="send_note"),
    path("createnote/", views.create_note, name="create_note"),
    path("detailnote/<int:note_pk>/", views.detail_note, name="detail_note"),
    path("detailnote/<int:note_pk>/delete", views.delete_note, name="delete_note"),
    # path("<int:pk>/delete/", views.delete, name="delete"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("passwordchange/", views.change_password, name="change_password"),
    path("<int:pk>/pwcheck_delete/", views.delete_checker, name="pw_check"),
    path("<int:pk>/delete/", views.social_delete, name="delete"),
    path("login/github/", views.github_login, name="github-login"),
    path("login/github/callback/", views.github_login_callback, name="github-callback"),
    path("<int:user_pk>/followers/", views.follow, name="follow"),
]
