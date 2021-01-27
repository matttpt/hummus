from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import RedirectView
from django.views.static import serve

from . import settings


def default_home(request):
    return render(request, "base.html", {"title": "Home"})


# This is installed to /login, so that the @login_required decorator
# (which redirects to /login) continues to work when OIDC is enabled
class RedirectToOIDCLoginView(RedirectView):
    pattern_name = "oidc_authentication_init"
    permanent = True
    query_string = True  # So that the "next" parameter is preserved


def logged_out_with_oidc(request):
    return render(request, "registration/logged_out.html")


# Views for accessing uploaded media, depending on how that is
# configured
if settings.SERVE_MEDIA:

    @login_required
    def serve_media(*args, **kwargs):
        kwargs["document_root"] = settings.MEDIA_ROOT
        return serve(*args, **kwargs)


elif settings.MEDIA_X_ACCEL_REDIRECT_URL:

    @login_required
    def x_accel_redirect_media(request, path):
        response = HttpResponse()
        response["X-Accel-Redirect"] = settings.MEDIA_X_ACCEL_REDIRECT_URL + path
        response["Content-Type"] = ""
        return response
