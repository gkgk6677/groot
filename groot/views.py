from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import User
from django.utils import timezone

# Create your views here.

def groot(request):
    return render(request, 'groot/main.html', {})

def login(request):
    if request.method =='GET':
        return render(request, 'groot/login.html', {})
    else:
        user_id = request.POST['user_id']
        user_pw = request.POST['user_pw']

        try:
            User.objects.get(user_id=user_id, user_pw=user_pw)
        except User.DoesNotExist:
            return HttpResponse('ID와 Password를 확인해주세요.')
        else:
            request.session['user_id'] = user_id
            return HttpResponse('로그인 하셨습니다.')

def logout(request) :
    del request.session['user_id']
    # return render(request, 'protect/home.html', {})
    # return redirect('main')
    return HttpResponse('로그아웃 하셨습니다.')

def join(request):
    if request.method == 'GET':
        return render(request, 'groot/join.html', {})
    else:
        user_id = request.POST['user_id']
        user_pw = request.POST['user_pw']
        com_num = request.POST['com_num']
        com_name = request.POST['com_name']
        com_head = request.POST['com_head']
        email = request.POST['email']
        address = request.POST['address']
        phone_num = request.POST['phone_num']

        user = User(user_id=user_id, user_pw=user_pw, com_num=com_num, com_name=com_name, com_head=com_head, email=email, address=address, phone_num=phone_num)
        user.c_date = timezone.now()
        user.save()

        return HttpResponse( user_id + '님 회원가입이 완료되었습니다.')



def mypage(request):
    return render(request, 'groot/mypage.html', {})


def list(request):
    return render(request, 'groot/list.html', {})

