import datetime
import hashlib
import json
import os
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
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import FormView
from django.db.models import Q

import calendar
import pandas
import random

# html2pdf 위한 라이브러리
from django.views.generic import View
# from .render import render_to_pdf
# import pdfkit
# import os

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
        s = request.POST['s']
        try:
            a = Extend.objects.get(enroll_idx=s)
            if a.status == 0 :
                # 연장 신청이 안되는 경우
                ck_val = 0
                context = {'ck_val': ck_val}

                return HttpResponse(json.dumps(context), content_type='application/json')
            else :
                ck_val =1
                context = {'ck_val': ck_val}

                return HttpResponse(json.dumps(context), content_type='application/json')

        except Extend.DoesNotExist:
            ck_val= 1
            context = {'ck_val': ck_val}
            return HttpResponse(json.dumps(context), content_type='application/json')

@csrf_exempt
def login3(request):
    if request.method == "POST":
        s = request.POST['s']
        try:
            a = Expire.objects.get(enroll_idx=s)
            if a.status == 0:
                # 해지 신청이 진행중이므로 안되는 경우
                ck_val = 0
                context = {'ck_val': ck_val}

                return HttpResponse(json.dumps(context), content_type='application/json')
            else:
                ck_val = 0
                context = {'ck_val': ck_val}
                # 해지 테이블에 값이 존재하므로 해지 신청 불가
                return HttpResponse(json.dumps(context), content_type='application/json')
        except Expire.DoesNotExist:
            try:
                b = Contract.objects.get(enroll_idx=s)
                if b.status == 0 or b.status == 1:
                    # 기술 계약이 진행중일때 해지 신청 불가
                    ck_val = 3
                    context = {'ck_val': ck_val}
                    return HttpResponse(json.dumps(context), content_type='application/json')
            except Contract.DoesNotExist:
                ck_val = 1
                context = {'ck_val': ck_val}
                return HttpResponse(json.dumps(context), content_type='application/json')


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

            enrollment.title = form.cleaned_data['title']
            enrollment.sort_idx = SortMst.objects.get(sort_idx = request.POST['sort_idx']) # SortMst에 들어가면서 문자로 바뀜
            enrollment.term = form.cleaned_data['term']
            enrollment.user_id = User()
            enrollment.user = u
            enrollment.enroll_status = 0
            enrollment.agree_status = request.POST['agree_radio']
            enrollment.c_date = datetime.datetime.now()
            enrollment.summary = form.cleaned_data['summary']
            # enrollment.end_date = datetime.datetime.now() + datetime.timedelta(days=365 * int(request.POST['term']))
            enrollment.save()

            user_foldername = request.session.get('user_id')
            com_foldername = u.com_name
            user_enrollidx = Enrollment.objects.filter(user_id=user_foldername).order_by('-pk')[0]
            files = request.FILES.getlist('my_file')
            flist = request.POST['listing']
            hashSHA = hashlib.sha256

            try:

                fpath = 'uploaded_files/' + str(user_foldername) + '/' + str(user_enrollidx.enroll_idx)
                os.makedirs(fpath, exist_ok=True)
                fpath = 'uploaded_files/'+str(enrollment.sort_idx.sort_idx)+'/' + str(com_foldername) + '/' + str(enrollment.title) #str(user_enrollidx.enroll_idx)                os.makedirs(fpath, exist_ok=True)
                # os.chdir(fpath)

                flists = flist.split(";")
                for i in range(len(flists) - 1):
                    rpath = fpath + '/' + flists[i]
                    print(rpath, os.path.dirname(rpath))
                    os.makedirs(os.path.dirname(rpath), exist_ok=True)

                    with open(rpath, "wb") as f:
                        for c in files[i].chunks():
                            f.write(c)

                    with open(rpath, 'r') as f:
                        textdata = f.read()

                   # with open(rpath, 'r') as f:
                   #     textdata = f.read()

                    dbfile = File()
                    dbfile.enroll_idx = Enrollment.objects.get(enroll_idx=user_enrollidx.enroll_idx)
                    dbfile.pid = rpath
                    dbfile.mid = hashSHA(textdata.encode('utf-8')).hexdigest()
                    dbfile.r_name = files[i].name
                    dbfile.save()

                    #dbfile.mid = hashSHA(textdata.encode('utf-8')).hexdigest()
                    dbfile.r_name = files[i].name
                    dbfile.save()

            except FileExistsError as e:
                pass
                # data = f.read()
                # hashSHA(data).hexdigest()

            value = {'enroll_tech': user_enrollidx.title}
            template = get_template('groot/application_complete.html')
            output = template.render(value)

            #    0          1        2         3        4        5       6          7            8           9
            # Technology   Sort   Company   Com_num   Term   Content   Client   Cont_term   Enroll_date   Status
            # fabric = "http://210.107.78.150:8000/add_cont/" + enrollment.title + "-" + sort_idx_tmp + "-" \
            #          + User.objects.get(user_id=request.session.get('user_id')).com_name + "-" \
            #          + str(User.objects.get(user_id=request.session.get('user_id')).com_num) + "-" \
            #          + enrollment.term + "-" + "Content" + "-" + "2019.01.14.1500" + "-" + "1"
            # f = requests.get(fabric)
            # print(f.text)  # cmd 창에 보여질 값
            return HttpResponse(output)

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
        fabric = "http://210.107.78.150:8001/change_term/" + enrollinfo.title + "@" \
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

def insert(request,idx):
    enrollinfo = Enrollment.objects.get(enroll_idx=idx)
    edate = date_format(enrollinfo.end_date,'Y년 m월 d일')
    contract = Contract()

    if request.method == 'POST':
        enrollinfo.term = request.POST['term']
        u = User.objects.get(user_id=request.session.get('user_id'))
        contract.user_id = User()
        form = ContractForm(request.POST)

        if form.is_valid():
            contract = Contract()
            contract.enroll_idx = enrollinfo
            contract.user_id = User()
            contract.user = u
            contract.term = form.cleaned_data['term']
            contract.status = 0
            contract.reason = form.cleaned_data['reason']
            contract.c_date = datetime.datetime.now()

            contract.save()

        return redirect('mypage')

    else:
        create_date = datetime.date.today()
        user = User.objects.get(user_id=request.session.get('user_id'))

        form = ContractForm()

    return render(request, 'groot/insert.html', {'user':user,'edate':edate,'enrollinfo': enrollinfo,'form': form,'create_date':create_date})



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

@my_login_required
@csrf_exempt
def issue(request):
    user_id = request.session['user_id']
    enroll_infos = Enrollment.objects.all().filter(user_id=user_id, enroll_status=1)
    contract_infos = Contract.objects.all().filter(user_id=user_id, status=1)

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

# class GeneratePdf(View) :
#     def get(self, request, *args, **kwargs):
#         template = get_template('groot/show_app.html')
#         html = template.render(kwargs)
#         # pdf = render_to_pdf('groot/show_app.html', kwargs)
#         return HttpResponse(pdf, content_type='application/pdf')

@csrf_exempt
def show_app(request, idx):
    user_id = request.session['user_id']

    enroll_info = Enrollment.objects.get(enroll_idx=idx)
    user = User.objects.get(user_id=user_id)
    cert_info = Certificate.objects.get(enroll_idx=idx, cont_idx=None)

    print(cert_info.cert_idx)

    # xhtml2pdf 이용
    # # file = show_app.html
    # html2pdf = GeneratePdf()
    # html2pdf.get(request, **value)
    # GeneratePdf.as_view()
    # return render_to_pdf('groot/show_app.html', {'enroll_info': enroll_info, 'user': user, 'cert_info': cert_info})

    return render(request, 'groot/show_app.html', {'enroll_info': enroll_info, 'user':user, 'cert_info':cert_info})

@csrf_exempt
def pdf_app(request, idx) :
    if request.method == 'POST' :
        user_id = request.session['user_id']
        idx = request.POST.get('idx')

        enroll_info = Enrollment.objects.get(enroll_idx=idx)
        user = User.objects.get(user_id=user_id)
        cert_info = Certificate.objects.get(enroll_idx=idx, cont_idx=None)

        value = {'enroll_info': enroll_info, 'user': user, 'cert_info': cert_info}
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }

        # template = get_template("groot/show_app.html")
        # html = template.render(value)
        pdf = pdfkit.from_file(r'C:\Users\어다희\work_django\groot-django\groot\templates\groot\show_app.html', False, options=options) # False로 속성을 지정하므로써 사용자가 원하는 이름으로 저장 가능!
        # url = request.get_host() + '/issue/show_app/' + str(idx) + '/pdf'
        # pdf = pdfkit.from_url(str(url), False, options=options) # False로 속성을 지정하므로써 사용자가 원하는 이름으로 저장 가능!
        # response = HttpResponse(pdf, content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename=임치증명서.pdf'

        return HttpResponse(pdf, content_type='application/pdf')

        # return HttpResponse(json.dumps(context), content_type='application/json')

    # if request.method == 'GET':
    #     return HttpResponse('get')

def show_cont(request, en_idx, cont_idx):
    user_id = request.session['user_id']

    enroll_info = Enrollment.objects.get(enroll_idx=en_idx)
    user = User.objects.get(user_id=user_id)
    contract = Contract.objects.get(cont_idx=cont_idx)
    cert_info = Certificate.objects.get(enroll_idx=en_idx, cont_idx=cont_idx)

    print(cert_info.cert_idx)

    return render(request, 'groot/show_cont.html', {'enroll_info': enroll_info, 'user': user, 'contract': contract, 'cert_info':cert_info})

def groot_scan(request):
    return render(request, 'groot/groot_scan.html', {})

def read(request):
    user_id = request.session['user_id']
    enroll_infos = Enrollment.objects.all().filter(user_id=user_id, enroll_status=1)
    contract_infos = Contract.objects.all().filter(user_id=user_id)

    if request.method == 'POST' :
        enroll_idx = request.POST.get('enroll_id')
        cont_idx = request.POST.get('cont_id')
        enroll_info = Enrollment.objects.get(enroll_idx=enroll_idx)
    else :
        return render(request, 'groot/read.html', {'enroll_infos': enroll_infos, 'contract_infos': contract_infos})


@my_login_required
def validate_intro(request):
    user_id = request.session['user_id']
    enroll_infos = Enrollment.objects.all().filter(user_id=user_id, enroll_status=1)

    return render(request, 'groot/validate_intro.html', {'enroll_infos': enroll_infos})

def validate_show(request):
    user_id = request.session['user_id']
    idx=41
    enroll_info = Enrollment.objects.get(enroll_idx=idx)

    if request.method == 'POST' :
        upload_file = request.FILES['validate_file']
        hashSHA = hashlib.sha256

        try:
            path = 'validate\\' + user_id + '\\' + str(idx)
            os.makedirs(path, exist_ok=True) # 다중파일 경로 생성(기존 파일이 존재해도 애러발생 안시킴)

            with open(path + '\\' + upload_file.name, 'wb') as file:  # 껍데기 파일을 만든 것!!(with로 열어주면 file.close() 안해줘도 됨 / with문 벗어나는 순간 자동 close됨)
                for chunk in upload_file.chunks():  # chunks가 호출되면 파일의 크기가 얼마든 다 쪼개냄
                    file.write(chunk)  # 그걸 for문으로 청크청크해서 write해줌(장고 공식문서에 나와있는 파일 업로드 하는 코드)
        except FileExistsError:
            pass
        else :
            with open(path + '\\' + upload_file.name, 'r') as file: # 읽기모드로 파일 꺼내옴
                textdata = file.read()

            mid = hashSHA(textdata.encode('utf-8')).hexdigest()
            name = upload_file.name
            print(mid)
            dbfiles = File.objects.filter(enroll_idx=idx) # DB상 파일의 등록번호가 같은 object들 꺼내오기

            for dbfile in dbfiles :
                if dbfile.r_name == name :
                    # valfile = File.objects.get(enroll_idx=idx, r_name=name) # DB상 파일의 등록번호와 업로드한 파일명이 같은 object 꺼내오기
                    if dbfile.mid == mid :
                        return HttpResponse('업로드 된 문서는 원본이 맞습니다.')
                    else :
                        return HttpResponse('업로드 된 문서는 위변조 되었습니다.')
                else :
                    return HttpResponse('해당 문서는 임치되지 않았습니다. 파일명을 다시 확인해주세요')

    else :
        return render(request, 'groot/validate_show.html', {})

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

def expire(request,idx):
    enrollinfo = Enrollment.objects.get(enroll_idx=idx)
    edate = date_format(enrollinfo.end_date,'Y년 m월 d일')
    if request.method == 'POST':
        e_date = enrollinfo.end_date
        form = ExpireForm(request.POST)

        if form.is_valid():
            expire = Expire()
            expire.enroll_idx = enrollinfo
            expire.status = 0
            expire.reason = form.cleaned_data['reason']
            expire.c_date = datetime.datetime.now()

            expire.save()

        return redirect('mypage')

    else:
        create_date = datetime.date.today()
        form = ExpireForm()

    return render(request, 'groot/expire.html', {'edate':edate,'enrollinfo': enrollinfo,'form': form,'create_date':create_date})

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
    app_info = Enrollment.objects.all().filter(enroll_status=1)

    if request.method == 'GET':
        return render(request, 'groot/search.html',{'app_info': app_info})



def upload(request):
    return render(request, 'groot/upload.html', {})
