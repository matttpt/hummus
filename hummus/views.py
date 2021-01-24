from django.shortcuts import redirect, render


def default_home(request):
    return render(request, "base.html", {"title": "Home"})


# This is installed to /login, so that the @login_required decorator
# (which redirects to /login) continues to work when OIDC is enabled
def redirect_to_oidc_login(request):
    return redirect("oidc_authentication_init", permanent=True)


def logged_out_with_oidc(request):
    return render(request, "registration/logged_out.html")
