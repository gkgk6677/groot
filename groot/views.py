import datetime
import json
from functools import wraps
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
import requests
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.template.loader import get_template
from django.urls import reverse
from django.utils.formats import date_format
from django.views.decorators.csrf import csrf_exempt
from groot.forms import EnrollmentForm
from groot.forms import *
from .models import *
from django.utils import timezone

from django.views.generic.edit import FormView
from django.db.models import Q

import calendar
import pandas
import random
# # html2pdf 위한 라이브러리
# from django.views.generic.base import View
# from .render import Render
# import os
# from django.conf import settings
# from django.template import Context
# from xhtml2pdf import pisa

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
    extend_info = Extend.objects.all()

    # return HttpResponse(enroll_infos)
    return render(request, 'groot/list.html', {'enroll_infos':enroll_infos, 'extend_info':extend_info})

@csrf_exempt
def login2(request):
    if request.method == "POST":
        idxx = request.POST['idx']
        extend_info = Extend.objects.get(enroll_idx = idxx)
        if extend_info.status == 0 :
            ck_val = 0
            # 연장신청햇음
        else :
            ck_val = 1

        context = {'ck_val': ck_val}
        return HttpResponse(json.dumps(context), content_type='application/json')
    if request.method =='GET':
        return HttpResponse('get')



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
        return redirect('/notice/ {new_notice.pk}')
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
            enrollment.title = form.cleaned_data['title']
            enrollment.sort_idx = SortMst.objects.get(sort_idx = request.POST['sort_idx']) # SortMst에 들어가면서 문자로 바뀜
            enrollment.term = form.cleaned_data['term']
            enrollment.user = u
            enrollment.enroll_status = 0
            enrollment.c_date = datetime.datetime.now()
            enrollment.summary = form.cleaned_data['summary']
            # enrollment.end_date = datetime.datetime.now() + datetime.timedelta(days=365 * int(request.POST['term']))
            enrollment.save()

            return HttpResponseRedirect(reverse('upload'))

    else:
        create_date = datetime.date.today()
        form = EnrollmentForm(initial={'c_date':create_date})
        user = User.objects.get(user_id=request.session.get('user_id'))
    return render(request, 'groot/application.html', {'form': form, 'user':user, 'create_date':create_date})

def extend(request,idx):
    enrollinfo = Enrollment.objects.get(enroll_idx=idx)
    edate = date_format(enrollinfo.end_date,'Y년 m월 d일')


    if request.method == 'POST':
        e_date = enrollinfo.end_date
        enrollinfo.term = request.POST['term']

        enrollinfo.end_date = e_date + datetime.timedelta(days=365 * int(request.POST['term']))
        # return HttpResponse(enrollment.end_date)
        enrollinfo.save()

        # Hyperledger-Fabric으로 데이터 전송@@@@@@@@@@@@
        #    0          1        2
        # Technology   Term   Status
        fabric = "http://210.107.78.150:8000/change_term/" + enrollinfo.title + "@" \
                 + enrollinfo.term + "@" + "3"
        f = requests.get(fabric)
        print(f.text)  # cmd 창에 보여질 값

        form = ExtendForm(request.POST)

        if form.is_valid():
            extend = Extend()
            extend.enroll_idx = enrollinfo
            extend.term = form.cleaned_data['term']
            extend.status = 0
            extend.reason = form.cleaned_data['reason']
            extend.c_date = datetime.datetime.now()

            extend.save()

        return redirect('mypage')

    else:
        create_date = datetime.date.today()

        form = ExtendForm()

    return render(request, 'groot/extend.html', {'edate':edate,'enrollinfo': enrollinfo,'form': form,'create_date':create_date})
#
# def extend(request,idx):
#
#     enrollinfo = Enrollment.objects.get(enroll_idx=idx)
#     extend_info= Extend()
#     enrollinfo.user_id = User()
#     enrollinfo.user = u
#
#     if request.method == 'POST':
#         extend_info.term = str(request.POST['term'])
#         extend_info.c_date = datetime.date.today()
#
#         # return HttpResponse(enrollment.end_date)
#         Extend.save()
#
#         # Hyperledger-Fabric으로 데이터 전송@@@@@@@@@@@@
#         #    0          1        2
#         # # Technology   Term   Status
#         # fabric = "http://210.107.78.150:8001/change_term/" + enrollinfo.title + "-" \
#         #          + enrollinfo.term + "-" + "3"
#         # f = requests.get(fabric)
#         # print(f.text)  # cmd 창에 보여질 값
#         # return redirect('mypage')
#     else:
#
#         # user = User.objects.get(user_id=request.session.get('user_id'))
#
#     return render(request, 'groot/extend.html', { 'enrollinfo': enrollinfo,'extend_info':extend_info})

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

@csrf_exempt
def issue(request):
    user_id = request.session['user_id']
    enroll_infos = Enrollment.objects.all().filter(user_id=user_id)
    contract_infos = Contract.objects.all().filter(user_id=user_id)

    if request.method == 'POST' :
        enroll_idx = request.POST.get('enroll_id')
        cont_idx = request.POST.get('cont_id')
        enroll_info = Enrollment.objects.get(enroll_idx=enroll_idx)

        # Hyperledger-Fabric에서 데이터 받아오기
        #    0          1        2         3        4        5       6          7            8          9
        # Technology   Sort   Company   Com_num   Term   Content   Client   Cont_term   Enroll_date   Status
        fabric = "http://210.107.78.150:8001/generate_cert/" + enroll_info.title
        result = requests.get(fabric)

        parses = result.json()  # JSON형식으로 parse(분석)
        block = None
        # [
        #   {
        #       "TxId":"d15ce93db3c2d73297c28734e973e88e26a89f58781b9a886311c12604ce340e",
        #       "Value":{
        #                  "technology":"TEST2","sort":13,
        #                   "company":"LG","com_num":156181987,"term":5,
        #                   "content":["sldkfjs"],
        #                   "client":{
        #                       "dahee":3
        #                   },
        #                  "enroll_date":"2018.01.11",
        #                  "status":1,
        #       },
        #       "Timestamp":"2019-01-11 08:05:45.948 +0000 UTC",
        #       "IsDelete":"false"
        #   },
        #   { ... }, { ... }, ...
        #  ]

        try :
            # 임치 증명서 일 때
            if cont_idx == "0" :
                ck_val = 1
                type = 0
                for parse in parses:
                    txid = parse.get('TxId')
                    if txid == enroll_info.enroll_tx : # txid가 DB에 저장되어있는 enroll_tx와 일치 할 경우 해당 JSON을 block에 저장!
                        block = parse

                cert_info = Certificate.objects.get(enroll_idx=enroll_idx, cont_idx=None)
                if cert_info.end_date <= datetime.datetime.now():
                    ck_val = 2  # 유효기간보다 날짜가 더 크면 만료

            # 계약 증명서 일 때
            elif cont_idx != "0" :
                cont_info = Contract.objects.get(cont_idx=cont_idx)
                ck_val = 1
                type = 1

                for parse in parses:
                    txid = parse.get('TxId')
                    if txid == cont_info.contract_tx : # txid가 DB에 저장되어있는 cont_tx와 일치 할 경우 해당 JSON을 block에 저장!
                        block = parse

                cert_info = Certificate.objects.get(enroll_idx=enroll_idx, cont_idx=cont_idx)
                if cert_info.end_date <= datetime.datetime.now():
                    ck_val = 2

        except Certificate.DoesNotExist:
            ck_val = 0

            certificate = Certificate()
            certificate.enroll_idx = Enrollment.objects.get(enroll_idx=enroll_idx)  # foreign key이므로!
            if cont_idx != "0" :
                certificate.cont_idx = Contract.objects.get(cont_idx=cont_idx)  # foreign key이므로!
            else :
                pass
            certificate.term = 7
            certificate.c_date = datetime.datetime.now()
            certificate.end_date = datetime.datetime.now() + datetime.timedelta(days=7)

            # 난수 생성해 저장하는 과정(str로 변환 후 각각 쪼개서(list로 만들고) random.sample 함수 돌리기
            unix_time = calendar.timegm(certificate.c_date.utctimetuple())  # timestamp로 변환
            unix_time = [str(i) for i in str(unix_time)]
            tx = block.get('TxId')
            tx = [str(i) for i in str(tx)]
            random_val = unix_time + tx
            random_val = random.sample(random_val, len(random_val))
            certificate.cert_idx = ''.join(random_val)

            print(''.join(random_val))
            certificate.save()

        context = {'ck_val':ck_val, 'type':type}
        return HttpResponse(json.dumps(context), content_type='application/json')

    else :
        return render(request, 'groot/issue.html', {'enroll_infos': enroll_infos, 'contract_infos': contract_infos})

# class Pdf(View):
def show_app(request, idx):
    user_id = request.session['user_id']

    enroll_info = Enrollment.objects.get(enroll_idx=idx)
    user = User.objects.get(user_id=user_id)
    cert_info = Certificate.objects.get(enroll_idx=idx, cont_idx=None)

    print(cert_info.cert_idx)

    # params = {'enroll_info': enroll_info, 'user':user, 'cc':block, 'request':request}
    # return Render.render('groot/show_app.html', params)

    return render(request, 'groot/show_app.html', {'enroll_info': enroll_info, 'user':user, 'cert_info':cert_info})

def show_cont(request, en_idx, cont_idx):
    user_id = request.session['user_id']

    enroll_info = Enrollment.objects.get(enroll_idx=en_idx)
    user = User.objects.get(user_id=user_id)
    contract = Contract.objects.get(cont_idx=cont_idx)
    cert_info = Certificate.objects.get(enroll_idx=en_idx, cont_idx=cont_idx)

    print(cert_info.cert_idx)

    return render(request, 'groot/show_cont.html', {'enroll_info': enroll_info, 'user': user, 'contract': contract, 'cert_info':cert_info})

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


######################TEST
class SearchFormView(FormView):
    form_class = SearchForm
    template_name = 'groot/search.html'

    def form_valid(self, form):
        schWord = self.request.POST['search_word']
        user_list = User.objects.filter(Q(user_id__icontains=schWord)).distinct()

        context = {}
        context['form'] = form
        context['search_term'] = schWord
        context['object_list'] = user_list



        return render(self.request, self.template_name, context)




#########################TEST
def search_list(request):
    app_info = Status.objects.all().filter(enroll_status=1)

    if request.method == 'GET':
        return render(request, 'groot/search.html',{'app_info': app_info})



def upload(request):
    return render(request, 'groot/upload.html', {})
