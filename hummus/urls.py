from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

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


urlpatterns = (
    [home_urls]
    + auth_urls
    + [
        path("forum/", include("forum.urls")),
        path("admin/", admin.site.urls),
    ]
)
