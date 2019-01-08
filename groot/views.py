import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
import requests
from groot.forms import EnrollmentForm
from .models import *
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
    enroll_infos = Enrollment.objects.all().filter(user=user_id)

    # return HttpResponse(enroll_infos)
    return render(request, 'groot/list.html', {'enroll_infos':enroll_infos})


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



count=0
def notice_write(request):
    if request.method == 'POST':
        if request.POST['title'] != '' and request.POST['content'] != '':
            u = User.objects.get(user=request.session.get('user_id'))
            new_notice = Notice.objects.create(
                user= u,
                title=request.POST['title'],
                content = request.POST['content'],
                count = count,
                c_date = timezone.now(),
                m_date = timezone.now()
            )
        return redirect(f'/notice/ {new_notice.pk}')
    return render(request, 'groot/notice_write.html')
#

def notice_detail(request,pk):
    notice= Notice.objects.get(pk=pk)
    return render(request, 'groot/notice_detail.html', {'notice': notice})


def register(request):
    return render(request, 'groot/register.html', {})

def application(request):
    if request.method == 'POST':

        form = EnrollmentForm(request.POST)
        end_date = datetime.datetime.now() + datetime.timedelta(days=365 * int(request.POST['term']))
        # return HttpResponse(end_date)
        if form.is_valid():
            enrollment = Enrollment()
            u = User.objects.get(user_id=request.session.get('user_id'))
            enrollment.user_id = User()
            enrollment.title = request.POST['title']
            sort_idx_tmp = request.POST['sort_idx'] # 숫자로 값을 넘기기 위해 임시로 저장
            enrollment.sort_idx = SortMst.objects.get(sort_idx = request.POST['sort_idx']) # SortMst에 들어가면서 문자로 바뀜
            enrollment.term = request.POST['term']
            enrollment.user = u
            enrollment.end_date = datetime.datetime.now() + datetime.timedelta(days=365 * int(request.POST['term']))
            enrollment.save()

            # Hyperledger-Fabric으로 데이터 전송@@@@@@@@@@@@
            #    0          1        2         3        4        5       6          7            8
            # Technology   Sort   Company   Com_num   Term   Content   Client   Cont_term   Enroll_date
            # 주소는 때에 따라 변경(210.107.78.150)
            fabric = "http://210.107.78.150:8000/add_cont/" + enrollment.title + "-" + sort_idx_tmp + "-" \
                                                            + User.objects.get(user_id=request.session.get('user_id')).com_name + "-" \
                                                            + str(User.objects.get(user_id=request.session.get('user_id')).com_num) + "-" \
                                                            + enrollment.term + "-" + "Content" + "-" + "null" + "-" + "0" + "-" \
                                                            + "201901081400"
            f = requests.get(fabric)
            print(f.text) # cmd 창에 보여질 값
            return redirect('mypage')
    else:
        form = EnrollmentForm()
    return render(request, 'groot/application.html', {'form': form})

def test(request):
    return render(request, 'groot/test.html', {})

def issue(request):
    return render(request, 'groot/issue.html', {})

def show_app(request):
    return render(request, 'groot/show_app.html', {})

def show_cont(request):
    return render(request, 'groot/show_cont.html', {})

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

