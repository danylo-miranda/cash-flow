from django.shortcuts import render


def login_page(request):
    return render(request, "web/login.html")


def app_page(request):
    return render(request, "web/app.html")
