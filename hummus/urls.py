from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import settings, views


if settings.HOME_APP:
    home_urls = path("", include(settings.HOME_URLS))
else:
    home_urls = path("", views.default_home, name="home")

urlpatterns = [
    home_urls,
    path("forum/", include("forum.urls")),
    path("login", auth_views.LoginView.as_view(), name="login"),
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls),
]
