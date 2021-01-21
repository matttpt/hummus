from django.shortcuts import render


def default_home(request):
    return render(request, "base.html", {"title": "Home"})
