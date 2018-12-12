from django.shortcuts import render

# Create your views here.

def groot(request):
    return render(request, 'groot/main.html', {})

def login(request):
    return render(request, 'groot/login.html', {})

def join(request):
    return render(request, 'groot/join.html', {})

def mypage(request):
    return render(request, 'groot/mypage.html', {})


def list(request):
    return render(request, 'groot/list.html', {})

