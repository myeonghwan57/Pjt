from social_core.pipeline.partial import partial
from .models import User


@partial
def save_login_method(backend, user, response, *args, **kwargs):
    if backend.name == "google-oauth2":
        user = User.objects.get(pk=user.id)
        user.login_method = "google"
        user.save()
