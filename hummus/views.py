from django.shortcuts import render
from django.views.generic.base import RedirectView


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
