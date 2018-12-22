from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import User
from .models import Notice
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


rowsPerPage = 5
def notice(request):

    noticeList = Notice.objects.order_by('c_date')[0:5]
    current_page = 1
    totalCnt = Notice.objects.all().count()

    pagingHelperlns = pagingHelper();
    totalPageList = pagingHelperlns.getTotalPageList(totalCnt, rowsPerPage)
    print('totalPageList', totalPageList)

    return render(request, 'groot/notice.html',{'noticeList': noticeList,'totalCnt': totalCnt,
                                                 'current_page': current_page, 'totalPageList': totalPageList})

class pagingHelper:

    def getTotalPageList(self, total_cnt, rowsPerPage):
        if ((total_cnt % rowsPerPage == 0)):
            self.total_pages = total_cnt // rowsPerPage;
            print('getTotalPage #1')
        else:
            self.total_pages = (total_cnt // rowsPerPage) + 1;
            print('getTotalPage #2')

        self.totalPageList = []
        for j in range(self.total_pages):
            self.totalPageList.append(j + 1)

        return self.totalPageList

    def __init__(self):
        self.total_pages = 0
        self.totalPageList = 0

# DB연동 @@@@@@@@@@@@@@@@@@@@@@@@@
# def notice_write(request):
#     nw= Notice(title=request.POST['title'],
#                 user_user=request.POST['user_user'],
#                 content=request.POST['content'],
#                 c_date=timezone.now(),
#                 count=0
#                 )
#
#     nw.save()
#     url = '/notice?current_page=1'
#     return HttpResponse(url)

count=0
def notice_write(request):
    if request.method == 'POST':
        if request.POST['title'] != '' and request.POST['content'] != '':
            new_notice = Notice.objects.create(
                title = request.POST['title'],
                user_user= request.session.user_id,
                content = request.POST['content'],
                count =+ count,
                c_date = timezone.now()
            )
            return redirect(f'/notice/{ new_notice.pk }')

        return render(request, 'groot/notice_write.html',{})

# def notice_write(request):
#     if request.method =='GET':
#         return render(request, 'groot/notice_write.html', {})
#     else:
#         title = request.POST['title']
#         content = request.POST['content']
#
#
#         notice = Notice( title=title, content=content)
#         notice.c_date = timezone.now()
#         notice.save()
#
#
#         return HttpResponse(title + '게시글 작성 완료')

def register(request):
    return render(request, 'groot/register.html', {})

def application(request):
    return render(request, 'groot/application.html', {})

def test(request):
    return render(request, 'groot/test.html', {})

def issue(request):
    return render(request, 'groot/issue.html', {})

def read(request):
    return render(request, 'groot/read.html', {})

def validate(request):
    return render(request, 'groot/validate.html', {})

def news(request):
    return render(request, 'groot/news.html', {})

