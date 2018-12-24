from django.http import HttpResponse
from django.shortcuts import render, redirect

from groot.forms import ContractForm
from .models import User, Contract
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
    return redirect('main')

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
    user_id = request.session['user_id']
    userinfo = User.objects.get(pk=user_id)
    return render(request, 'groot/mypage.html', {'userinfo':userinfo})


def list(request):
    user_id = request.session['user_id']
    contract_info = Contract.objects.get(user_user=user_id)
    return render(request, 'groot/list.html', {'contract_info':contract_info})


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
    if request.method == 'POST':
        form = ContractForm(request.POST)
        user_id = request.session['user_id']

        if form.is_valid():
            contract = Contract()
            u = User.objects.get(user_id=request.session.get('user_id'))
            contract.user_user = User()
            contract.title = form.cleaned_data['title']
            contract.sort = form.cleaned_data['sort']
            contract.e_date = form.cleaned_data['e_date']
            contract.user_user = u
            contract.save()

            return redirect('mypage')


    else:
        form = ContractForm()
    return render(request, 'groot/application.html', {'form': form})


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

def faq(request):
    return render(request, 'groot/faq.html', {})

def qna(request):
    return render(request, 'groot/qna.html', {})

def bye(request):
    return render(request, 'groot/bye.html', {})

def extend(request):
    return render(request, 'groot/extend.html', {})

def insert(request):
    return render(request, 'groot/insert.html', {})

def expire(request):
    return render(request, 'groot/expire.html', {})

