import datetime
import json
from functools import wraps
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from django.shortcuts import render, redirect
from django.template import RequestContext
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
import requests
from groot.forms import EnrollmentForm
from groot.forms import *
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
            if user_id == 'admin':
                request.session['user_id'] = user_id
                return HttpResponse('관리자 페이지로 접속합니다.')
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
        user_pw = request.POST['user_pw1']
        com_num = request.POST['com_num']
        com_name = request.POST['com_name']
        com_head = request.POST['com_head']
        email = request.POST['email']
        address = request.POST['address']
        phone_num = request.POST['phone_num']

        user = User(user_id=user_id, user_pw=user_pw, com_num=com_num, com_name=com_name, com_head=com_head, email=email, address=address, phone_num=phone_num)
        user.status = 0
        user.s_date = timezone.now()
        user.save()

        value = {'user_id': user_id}
        template = get_template('groot/welcome.html')
        output = template.render(value)

        return HttpResponse(output)


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
                m_date = timezone.now(),
            )
        return redirect(f'/notice/ {new_notice.pk}')
    return render(request, 'groot/notice_write.html')
#

def notice_detail(request,pk):
    notice= Notice.objects.get(pk=pk)
    return render(request, 'groot/notice_detail.html', {'notice': notice})


def register(request):
    return render(request, 'groot/register.html', {})

#login required decorator
def my_login_required(func):
        @wraps(func)
        def wrap(request, *args, **kwargs):
                #this check the session
                id = request.session.get('user_id');
                if bool(id) != True:
                    return redirect ('login')
                return func(request, *args, **kwargs)
        return wrap

@my_login_required
def application(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
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
            enrollment.c_date = datetime.datetime.now()
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
            print(f.text)  # cmd 창에 보여질 값
            return redirect('mypage')
    else:
        form = EnrollmentForm()
    return render(request, 'groot/application.html', {'form': form})

def extend(request,idx):
    user_id = request.session['user_id']
    # enrollinfo = Enrollment.objects.filter(user_id=user_id)

    enrollinfo = Enrollment.objects.get(enroll_idx=idx)

    if request.method == 'POST':

        # enrollment = Enrollment()
        e_date = enrollinfo.end_date
        enrollinfo.term = request.POST['term']

        enrollinfo.end_date = e_date + datetime.timedelta(days=365 * int(request.POST['term']))
        # return HttpResponse(enrollment.end_date)
        enrollinfo.save()

        return redirect('mypage')
    else:
        return render(request, 'groot/extend.html', {'enrollinfo': enrollinfo})

@csrf_exempt
# @csrf_protect
def idcheck(request):
    find_userid = request.POST['userid']

    if User.objects.filter(user_id = find_userid) :
        ck_val = 1
    else:
        ck_val = 0

    context = {'ck_val': ck_val}
    return HttpResponse(json.dumps(context), content_type='application/json')

def insert(request):
    user_id = request.session['user_id']
    # enrollinfo = Enrollment.objects.get(user_id=user_id)

    enrollinfo = Enrollment.objects.filter(name_id=user_id)
    # .order_by('-update_date')

    if request.method == 'POST':
        form = EnrollmentForm(request.POST)

        if form.is_valid():
            enrollment = Enrollment()
            e_date = enrollinfo.end_date

            enrollment.term = request.POST['term']
            enrollment.end_date = e_date + datetime.timedelta(days=365+365 * int(request.POST['term']))

            # return HttpResponse(enrollment.end_date)
            # 업 데 이 트 하 는 방 법 이 필 요 해 !
            form.save()
            enrollment.save()

        return redirect('mypage')

@csrf_exempt
def com_num_check(request):
    find_num = request.POST['com_num']

    if User.objects.filter(com_num = find_num) :
        com_ck_val = 1
    else:
        com_ck_val = 0

    context = {'com_ck_val': com_ck_val}
    return HttpResponse(json.dumps(context), content_type='application/json')
    #     form = EnrollmentForm()
    # return render(request, 'groot/insert.html', {'form': form, 'enrollinfo': enrollinfo})

#
# class SearchFormView():
#     form_class= SearchForm
#     template_name = 'groot/insert.html'
#
#     def form_valid(self, form):
#         word = '%s' %self.request.POST['word']
#         com_list = Enrollment.objects.filter(
#             Q(com_name__icontains=word)
#         ).distinct()
#         context = {}
#         context['object_list']= com_list
#         context['search_word']=word
#         return context

def change(request):
    return render(request, 'groot/change.html', {})

def change_pw(request):

    userinfo = User.objects.get(user_id=request.session.get('user_id'))

    if request.method == 'GET':
        return render(request, 'groot/change_pw.html', {'userinfo':userinfo})
    else:
        user_pw = request.POST['confirm_pw']
        new_pw1 = request.POST['new_pw1']
        new_pw2 = request.POST['new_pw2']
        if user_pw == userinfo.user_pw:
            if new_pw1 == new_pw2:
                userinfo.user_pw = new_pw1
                userinfo.save()
                return redirect('change')
            else: 
                return HttpResponse("두 비밀번호가 다릅니다.")
        else:
            return HttpResponse("기존 비밀번호가 다릅니다.")

def change_com(request):

    cominfo = User.objects.get(user_id=request.session.get('user_id'))

    if request.method =='GET':
        return render(request, 'groot/change_com.html', {'cominfo':cominfo})
    else:
        email = request.POST['email']
        address = request.POST['address']
        phone_num = request.POST['phone_num']
 
        if email != '':
            cominfo.email = email
        if address != '':
            cominfo.address = address
        if phone_num != '':
            cominfo.phone_num = phone_num
        cominfo.save()

        return redirect('change')
    

def test(request):
    return render(request, 'groot/test.html', {})

def issue(request):
    user_id = request.session['user_id']
    contract_infos = Contract.objects.all().filter(user_id=user_id)
    # contract_infos = Contract.objects.filter(user_id=user_id)
    # contract_infos = Contract.objects.filter(enroll_idx__in=Subquery(enroll_infos.values('enroll_idx'))) 서브쿼리도 안됨
    # contract_infos = Contract.objects.filter(enroll_idx__name=Enrollment('enroll_idx')) 다른 데이터필드 간 비교도 안됨

    # for enroll_info in enroll_infos :
    #     contract_info = Contract.objects.filter(enroll_idx=enroll_info.enroll_idx)
    #     contract_infos += contract_info 전역변수 에러 발생

    return render(request, 'groot/issue.html', {'contract_infos': contract_infos})

def show_app(request, idx):
    user_id = request.session['user_id']

    enroll_info = Enrollment.objects.get(enroll_idx=idx)
    user = User.objects.get(user_id=user_id)

    return render(request, 'groot/show_app.html', {'enroll_info': enroll_info, 'user':user})

def show_cont(request, en_idx, cont_idx):
    user_id = request.session['user_id']

    enroll_info = Enrollment.objects.get(enroll_idx=en_idx)
    user = User.objects.get(user_id=user_id)
    contract = Contract.objects.get(cont_idx=cont_idx)

    return render(request, 'groot/show_cont.html', {'enroll_info': enroll_info, 'user': user, 'contract': contract})

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

    userinfo = User.objects.get(user_id=request.session.get('user_id'))
    
    if request.method == 'GET':
        return render(request, 'groot/bye.html', {'userinfo':userinfo})
    else:
        password = request.POST['pw1']
        password_check = request.POST['pw2']

        del request.session['user_id']
        userinfo.delete() 
        
        return redirect('main')

def expire(request):
    return render(request, 'groot/expire.html', {})

def a(request):
    return render(request, 'groot/a.html', {})

