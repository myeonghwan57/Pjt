from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("<int:pk>/", views.detail, name="detail"),
    path("update/", views.update, name="update"),
    path("<int:pk>/delete/", views.delete, name="delete"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("passwordchange/", views.change_password, name="change_password"),
]
