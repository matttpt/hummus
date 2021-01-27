import re

from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path

from . import settings, views


# Use a custom home app if one is provided, otherwise render a home page
# with no content
if settings.HOME_APP:
    home_urls = path("", include(settings.HOME_URLS))
else:
    home_urls = path("", views.default_home, name="home")


# Our authentication URL configuration depends on whether OIDC is
# enabled or not
if settings.USE_OIDC:
    auth_urls = [
        path("login", views.RedirectToOIDCLoginView.as_view(), name="login"),
        path("logged-out", views.logged_out_with_oidc),
        path("oidc/", include("mozilla_django_oidc.urls")),
    ]
else:
    auth_urls = [
        path("login", auth_views.LoginView.as_view(), name="login"),
        path("logout", auth_views.LogoutView.as_view(), name="logout"),
    ]


# Serve our own uploaded media if we are asked to do so (in debug mode
# only). Otherwise, we assume we are behind a proxy, and we send the
# X-Accel-Redirect header back to it if the proper URL is provided.
if settings.SERVE_MEDIA:
    media_urls = static(settings.MEDIA_URL, view=views.serve_media)
elif settings.MEDIA_X_ACCEL_REDIRECT_URL:
    media_urls = [
        re_path(
            r"^{}(?P<path>.*)$".format(re.escape(settings.MEDIA_URL.lstrip("/"))),
            views.x_accel_redirect_media,
        )
    ]
else:
    media_urls = []


urlpatterns = (
    [home_urls]
    + auth_urls
    + media_urls
    + [
        path("forum/", include("forum.urls")),
        path("admin/", admin.site.urls),
    ]
)
