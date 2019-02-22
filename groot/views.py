import datetime
import hashlib
import json
import operator
import os
from functools import wraps, reduce
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
import requests
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.template.loader import get_template
from django.urls import reverse
from django.utils.formats import date_format
from django.views.decorators.csrf import csrf_exempt

from blockchain import settings
from groot.forms import EnrollmentForm
from groot.forms import *
from .models import *
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import FormView
from django.db.models import Q
import zipfile
import calendar
import pandas
import random
from urllib.parse import quote

# html2pdf 위한 라이브러리
from django.views.generic import View
from .render import Render
import os

# groot_Scan 위한 라이브러리
import matplotlib.pyplot as plt # 그래프
import sys # 블록 크기

from cryptography.fernet import Fernet
import pyotp

# query문 날리기 위한 라이브러리
from django.db import connection
from collections import namedtuple

# Create your views here.


def groot(request):
    try:
        request.session['user_id']
    except KeyError:
        return render(request, 'groot/main.html', {})
    else:
        userinfo = request.session['user_id']
        return render(request, 'groot/main.html', {'userinfo':userinfo})


    # if request.session['user_id']:
    #     userinfo = request.session['user_id']
    #     return render(request, 'groot/main.html', {'userinfo':userinfo})
    # else:
    #     return render(request, 'groot/main.html', {})

def login(request):
    if request.method =='GET':
        return render(request, 'groot/login.html', {})
    else: #POST
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
                userinfo = User.objects.get(user_id=user_id)
                if userinfo.otp == 'Issued':
                    return HttpResponse('OTP입력 페이지로 이동합니다.')
                elif userinfo.otp == None:
                    request.session['user_id'] = user_id
                    return HttpResponse('로그인 하셨습니다.')

def login_otp(request):
    user_id = request.POST['user_id']
    key = b'PvyhpBY3ACtXhj_wm9ueKhFSYyKAz4ntMc3p6sKYvuI='
    cipher_suite = Fernet(key)
    with open('otp/%s.bin' % user_id, 'rb') as file_object:
        for line in file_object:
            encryptedpwd = line
    uncipher_text = cipher_suite.decrypt(encryptedpwd)
    otpkey = bytes(uncipher_text).decode("utf-8")
    totp = pyotp.TOTP(otpkey)
    nowotp = totp.now()

    if request.method == 'GET':
        return render(request, 'groot/login_otp.html',{})
    else:
        otp = request.POST['otp']
        if otp == nowotp:
            request.session['otp'] = 'true'
            request.session['user_id'] = user_id
            return HttpResponse('로그인 되었습니다.')
        else:
            return HttpResponse('OTP 인증번호를 다시 확인해주십시오.')

def mypage_otp(request):
    user_id = request.session['user_id']
    key = b'PvyhpBY3ACtXhj_wm9ueKhFSYyKAz4ntMc3p6sKYvuI='
    cipher_suite = Fernet(key)
    with open('otp/%s.bin' % user_id, 'rb') as file_object:
        for line in file_object:
            encryptedpwd = line
    uncipher_text = cipher_suite.decrypt(encryptedpwd)
    otpkey = bytes(uncipher_text).decode("utf-8")
    totp = pyotp.TOTP(otpkey)
    nowotp = totp.now()
    otpsave = User.objects.get(user_id=user_id)
    otp = request.POST['otp']
    if otp == nowotp:
        otpsave.otp = 'Issued'
        otpsave.save()
        del request.session['user_id']
        return HttpResponse('로그인 되었습니다.')
    else:
        return HttpResponse('OTP 인증번호를 다시 확인해주십시오.')

def need_otp(request):
    try:
        request.session['user_id']
    except KeyError:
        return HttpResponse('false')
    else:
        try:
            request.session['otp']
        except KeyError:
            return HttpResponse('해당 서비스는 OTP를 발급 받은 후 사용하실 수 있습니다. Mypage    에서 OTP를 발급받아주세요.   (문의 : groot-admin@groot.co.kr)')
        else:
            return HttpResponse('true')

def need_login(request):
    try:
        request.session['user_id']
    except KeyError:
        return HttpResponse('false')
    else:
        return True

def logout(request) :
    try:
        request.session['otp']
    except KeyError:
        del request.session['user_id']
        return HttpResponse('로그아웃 되었습니다.')
    else:
        del request.session['user_id']
        del request.session['otp']
        return HttpResponse('로그아웃 되었습니다.')

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
        homepage = request.POST['homepage']

        revised_com_num = com_num[0:3] + '-' + com_num[3:5] + '-' + com_num[5:10]
        revised_phone_num = phone_num[0:3] + '-' + phone_num[3:7] + '-' + phone_num[7:11]

        user = User(user_id=user_id, user_pw=user_pw, com_num=revised_com_num, com_name=com_name, com_head=com_head, email=email, address=address, phone_num=revised_phone_num, homepage=homepage)
        user.status = 0
        user.s_date = timezone.now()
        user.save()

        value = {'user_id': user_id, 'com_head':com_head}
        template = get_template('groot/welcome.html')
        output = template.render(value)

        return HttpResponse(output)


def mypage(request):
    user_id = request.session['user_id']
    userinfo = User.objects.get(pk=user_id)

    # 임치 현황 값 DB에서 불러오기
    enroll_lists = Enrollment.objects.all().filter(user=user_id, enroll_status=1)
    enroll_ready_lists = Enrollment.objects.all().filter(user=user_id, enroll_status=0)
    contract_infos = Contract.objects.all()
    extend_infos = Extend.objects.all()
    expire_infos = Expire.objects.all()
    now_date = datetime.datetime.now()
    enroll_count = 0
    enroll_ready_count = 0
    extend_count = 0
    contract_count = 0
    expire_count = 0
    contract_is_value = 0
    contract_count_for_me = 0

    # 임치 대기중 리스트
    for i in enroll_ready_lists:
        enroll_ready_count += 1

    # 임치 계약 수 계산
    for i in enroll_lists:
        if i.end_date > now_date:
            enroll_count += 1

    # 연장 현황 카운트

    for extend_info in extend_infos:
        if (extend_info.enroll_idx.user.user_id == user_id and extend_info.enroll_idx.enroll_status == 1 and extend_info.status == 0):
            extend_count += 1

    # 계약 신청 수 계산

    for contract_info in contract_infos:
        if (contract_info.user.user_id == user_id and contract_info.status == 0):
            contract_count += 1

    # 해지 현황 카운트

    for expire_info in expire_infos:
        if (expire_info.enroll_idx.user.user_id == user_id and expire_info.enroll_idx.enroll_status == 1 and expire_info.status == 0):
            expire_count += 1
    
    # 계약 현황 카운트

    for contract_info in contract_infos:
        if ((contract_info.enroll_idx.user.user_id == user_id and contract_info.status == 1) or (contract_info.user.user_id == user_id and contract_info.status == 1)):
            contract_is_value += 1

    # 내게 들어온 계약 신청 현황 카운트

    for contract_info in contract_infos:
        if (contract_info.enroll_idx.user.user_id == user_id and contract_info.enroll_idx.enroll_status == 1 and contract_info.status == 0):
            contract_count_for_me += 1

    return render(request, 'groot/mypage.html', {'enroll_ready_count':enroll_ready_count, 'userinfo':userinfo, 'contract_is_value':contract_is_value, 'contract_count_for_me':contract_count_for_me, 'expire_count':expire_count, 'extend_count':extend_count, 'user_id':user_id, 'contract_count':contract_count, 'enroll_count':enroll_count})

def otp_pwcheck(request):
    user_id = request.session['user_id']
    userinfo = User.objects.get(user_id=user_id)
    pw = request.POST['user_pw']
    if pw == userinfo.user_pw:
        del request.session['otp']
        userinfo.otp = None
        userinfo.save()
        return HttpResponse('성공')
    else:
        return HttpResponse('실패')

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
        ck_val = 0
        try:
            cont_info = Contract.objects.get(enroll_idx=s)
            if cont_info.status == 1:
                # 기술 계약이 진행중일때 해지 신청 불가
                ck_val = 1
                context = {'ck_val': ck_val}
                return HttpResponse(json.dumps(context), content_type='application/json')
        except Contract.DoesNotExist:
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


# -*- coding: utf-8 -*-
@csrf_exempt
def download(request, idx):
    def folder_zip(src_path, dest_file):
        with zipfile.ZipFile(dest_file, 'w') as zf:
            rootpath = src_path
            for (path, dir, files) in os.walk(src_path):
                for file in files:
                    fullpath = os.path.join(path, file)
                    relpath = os.path.relpath(fullpath, rootpath)
                    zf.write(fullpath, relpath, compress_type=zipfile.ZIP_DEFLATED)
            zf.close()

    enroll_id = idx
    enrollment = Enrollment.objects.get(enroll_idx=enroll_id)
    tpath = os.getcwd()

    filepath = os.path.join(settings.BASE_DIR, 'uploaded_files', str(enrollment.sort_idx.sort_idx),
                            enrollment.user.com_name, enrollment.title)
    dest = os.path.join(settings.BASE_DIR, 'uploaded_files/tmp') + '/' + enrollment.title + '.zip'
    folder_zip(filepath, dest)
    os.chdir(tpath)

    # filepath = os.path.join(settings.BASE_DIR, 'uploaded_files', str(enrollment.sort_idx.sort_idx) , enrollment.user.com_name, enrollment.title, enrollment.title + '.zip')

    zippath = os.path.join(settings.BASE_DIR, 'uploaded_files/tmp', enrollment.title + '.zip')
    fileName = os.path.basename(zippath)
    with open(zippath, 'rb') as f:
        response = HttpResponse(f, content_type='application/zip')
        # fileName = fileName.encode("utf-8")
        # try:
        #     fileName.encode('ascii')
        #     file_expr = 'filename="{}"'.format(fileName)
        # except UnicodeEncodeError:
        #     # Handle a non-ASCII filename
        file_expr = "filename*=utf-8''{}".format(quote(fileName))
        response['Content-Disposition'] = 'attachment; {}'.format(file_expr)
    os.remove(zippath)
    return response

@my_login_required
def application(request):
    try:
        request.session['otp']
    except KeyError:
        return redirect('/wrong')
    else:
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
                    fpath = 'uploaded_files/'+str(enrollment.sort_idx.sort_idx)+'/' + str(com_foldername) + '/' + str(enrollment.title) #str(user_enrollidx.enroll_idx)                
                    os.makedirs(fpath, exist_ok=True)
                    # os.chdir(fpath)

                    flists = flist.split(";")
                    for i in range(len(flists) - 1):
                        rpath = fpath + '/' + flists[i]
                        print(rpath, os.path.dirname(rpath))
                        os.makedirs(os.path.dirname(rpath), exist_ok=True)

                        with open(rpath, "wb") as f:
                            for c in files[i].chunks():
                                f.write(c)
                        with open(rpath, 'rb', encoding=None) as f:
                            textdata = f.read()

                        dbfile = File()
                        dbfile.enroll_idx = Enrollment.objects.get(enroll_idx=user_enrollidx.enroll_idx)
                        dbfile.folder_path = os.path.dirname(rpath)
                        dbfile.file_hash = hashSHA(textdata).hexdigest()
                        dbfile.file_name = files[i].name
                        dbfile.save()

                except FileExistsError as e:
                    pass

                return render(request, 'groot/application_complete.html', {'enroll_tech':user_enrollidx.title})

        else:
            create_date = datetime.date.today()
            form = EnrollmentForm(initial={'c_date':create_date})
            user = User.objects.get(user_id=request.session.get('user_id'))
        return render(request, 'groot/application.html', {'form': form, 'user':user, 'create_date':create_date})


def extend(request,idx):
    try:
        request.session['otp']
    except KeyError:
        return redirect('/wrong')
    else:
        enrollinfo = Enrollment.objects.get(enroll_idx=idx)
        edate = date_format(enrollinfo.end_date,'Y년 m월 d일')

        if request.method == 'POST':

            form = ExtendForm(request.POST)

            if form.is_valid():
                extend = Extend()
                extend.enroll_idx = enrollinfo
                extend.term = form.cleaned_data['term']
                extend.status = 0
                extend.reason = form.cleaned_data['reason']
                extend.c_date = datetime.datetime.now()
                extend.save()
                enrollinfo.extend_status = 'impossible'
                enrollinfo.save()

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
    try:
        request.session['otp']
    except KeyError:
        return redirect('/wrong')
    else:
        user_id = request.session['user_id']
        enroll_infos = Enrollment.objects.all().filter(user_id=user_id, enroll_status=1).order_by('-enroll_date')
        contract_infos = Contract.objects.all().order_by('-accept_date')
        cert_infos = Certificate.objects.all()
        cont_info = []
        cert_info = []
        cert_lists1 = [] # 임치 증명서에 쓰일 리스트
        cert_lists2 = [] # 계약 증명서에 쓰일 리스트
        flag1 = {} # 임치 증명서 발급유무를 따질 변수
        flag2 = {} # 계약 증명서 발급유무를 따질 변수

        for contract_info in contract_infos:
            if contract_info.enroll_idx.user.user_id == user_id and contract_info.status == 1:
                cont_info.append(contract_info)

        for c_info in cert_infos:
            if c_info.enroll_idx.user.user_id == user_id :
                cert_info.append(c_info)

        if request.method == 'POST' :
            enroll_idx = request.POST.get('enroll_id')
            cont_idx = request.POST.get('cont_id')
            enroll_info = Enrollment.objects.get(enroll_idx=enroll_idx)

            # Hyperledger-Fabric에서 데이터 받아오기
            #    0          1        2         3        4        5           6         7          8           9           10
            # Technology   Sort   Company   Com_num   Term   File_name   File_hash   Client   Cont_term   Enroll_date   Status
            fabric = "http://210.107.78.147:8001/get_cert_verify/" + enroll_info.title
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
                certificate.cert_status = 0
                if cont_idx != "0" :
                    certificate.cont_idx = Contract.objects.get(cont_idx=cont_idx)  # foreign key이므로!
                else :
                    pass
                certificate.term = 30
                certificate.c_date = datetime.datetime.now()
                certificate.end_date = datetime.datetime.now() + datetime.timedelta(days=30)

                # Hyperledger-Fabric에서 데이터 받아오기
                #    0          1        2         3        4        5           6         7          8           9           10
                # Technology   Sort   Company   Com_num   Term   File_name   File_hash   Client   Cont_term   Enroll_date   Status
                fabric = "http://210.107.78.147:8001/get_cert_verify/" + enroll_info.title
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
                    certificate.cert_status = 0
                    if cont_idx != "0" :
                        certificate.cont_idx = Contract.objects.get(cont_idx=cont_idx)  # foreign key이므로!
                    else :
                        pass
                    certificate.term = 30
                    certificate.c_date = datetime.datetime.now()
                    certificate.end_date = datetime.datetime.now() + datetime.timedelta(days=30)

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
            for enroll_info in enroll_infos : # 임치증명서 관련
                flag1[enroll_info.enroll_idx] = False
                for cert in cert_info :
                    if cert.cont_idx == None : # 임치증명서에 대해서만 실행
                        if enroll_info.enroll_idx == cert.enroll_idx.enroll_idx :
                            flag1[enroll_info.enroll_idx] = True
                            if cert.cert_status == 0 : # 발급된 상태
                                cert.cert_status = "<button class='btn btn-outline-danger ck_button disabled' style='padding: 6px 3px 6px 3px;font-size:80%; border-color:rgb(238, 89, 89); width:70px;text-align: center;'>발급완료</button>"
                            else : # 발급기간 만료
                                cert.cert_status = "<button class='btn btn-outline-danger ck_button disabled' style='padding: 6px 3px 6px 3px;font-size:80%; border-color:rgb(238, 89, 89); width:70px;text-align: center;'>기간만료</button>"
                            cert_lists1.append(cert)

            for cont in cont_info : # 계약증명서 관련
                flag2[cont.cont_idx] = False
                for cert in cert_info :
                    if cert.cont_idx != None : # 계약증명서에 대해서만 실행
                        if cont.cont_idx == cert.cont_idx.cont_idx :
                            flag2[cont.cont_idx] = True
                            if cert.cert_status == 0 : # 발급된 상태
                                cert.cert_status = "<button class='btn btn-outline-danger ck_button disabled' style='padding: 6px 3px 6px 3px;font-size:80%; border-color:rgb(238, 89, 89); width:70px;text-align: center;'>발급완료</button>"
                            else : # 발급기간 만료
                                cert.cert_status = "<button class='btn btn-outline-danger ck_button disabled' style='padding: 6px 3px 6px 3px;font-size:80%; border-color:rgb(238, 89, 89); width:70px;text-align: center;'>기간만료</button>"
                            cert_lists2.append(cert)

            return render(request, 'groot/issue.html', {'enroll_infos': enroll_infos, 'cont_infos': cont_info, 'cert_infos1':cert_lists1, 'flag1':flag1, 'cert_infos2':cert_lists2, 'flag2':flag2})

class app_pdf(View) :
    def get(self, request, idx, *args, **kwargs):
        user_id = request.session['user_id']
        user = User.objects.get(user_id=user_id)
        enroll_info = Enrollment.objects.get(enroll_idx=idx)
        cert_info = Certificate.objects.get(enroll_idx=idx, cont_idx=None)

        params = {'enroll_info': enroll_info, 'user': user, 'cert_info': cert_info}

        return Render.render('groot/show_app.html', params)

class cont_pdf(View):
    def get(self, request, en_idx, cont_idx, *args, **kwargs):
        user_id = request.session['user_id']
        user = User.objects.get(user_id=user_id)
        enroll_info = Enrollment.objects.get(enroll_idx=en_idx)
        contract = Contract.objects.get(cont_idx=cont_idx)
        cert_info = Certificate.objects.get(enroll_idx=en_idx, cont_idx=cont_idx)

        params = {'enroll_info': enroll_info, 'user': user, 'cert_info': cert_info, 'contract': contract}
        return Render.render('groot/show_cont.html', params)

def get_height() : # 블록높이 가져오는 함수
    # 전체 블록의 높이와 current_hash, previous_hash 얻어오기
    fabric_all_block = "http://210.107.78.147:8001/query_tech"
    result_height = requests.get(fabric_all_block)
    height_parse = result_height.json()

    height = height_parse.get('height').get('low')  # 현재 블록의 높이

    return height

def get_tx() : # 모든 tx 불러오는 함수
    groot_tscan = []
    transactions = ""
    height = get_height()

    for i in range(1, height):
        # Hyperledger-Fabric에서 각 Key 별 history 얻어오기
        fabric = "http://210.107.78.147:8001/query_block/" + str(i)
        result = requests.get(fabric)
        block_parse = result.json()

        block_number = block_parse.get('info').get('block_number')
        for j in range(0, len(block_parse.get('data'))) :
            timestamp = block_parse.get('data')[j]['Timestamp'][0:-5]
            timestamp = timestamp.split('T')
            timestamp = ' '.join(timestamp)
            timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            timestamp = timestamp + datetime.timedelta(hours=9)

            txid = block_parse.get('data')[j].get('Transaction_ID')

            transactions = {"timestamp": timestamp, "txid": txid}

        groot_tscan.append([{"block_number": block_number, "transactions":transactions}])

    groot_tscan = sorted(groot_tscan, key=lambda k: k[0].get('transactions').get('timestamp'), reverse=True)  # 기본값은 false로 오름차순 정렬(reverse=True 옵션으로 내림차순 정렬)

    return groot_tscan

def get_block(n): # 블록정보를 가져오는 함수
    groot_bscan = []
    height = get_height()

    for i in range(height-n, height) :
        # Hyperledger-Fabric에서 각 Key 별 history 얻어오기
        fabric = "http://210.107.78.147:8001/query_block/" + str(i)
        result = requests.get(fabric)
        block_parse = result.json()

        block_num = block_parse.get('info').get('block_number')
        previous_hash = block_parse.get('info').get('previous_hash')
        data_hash = block_parse.get('info').get('data_hash')
        transactions = block_parse.get('info').get('transactions')

        timestamp = block_parse.get('data')[0]['Timestamp'][0:-5]
        timestamp = timestamp.split('T')
        timestamp = ' '.join(timestamp)
        timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        timestamp = timestamp + datetime.timedelta(hours=9)

        tx = block_parse.get('data')
        groot_bscan.append([{"block_number": block_num, "previous_hash": previous_hash, "data_hash": data_hash, "current_hash": None,
                             "timestamp": timestamp, "transactions": transactions, "data": tx}])

    for i in range(0, len(groot_bscan)) :
        if i == len(groot_bscan)-1 : # 마지막 블록에서 멈추기
            groot_bscan[i][0]["current_hash"] = groot_bscan[i][0].get('data_hash')
            break
        groot_bscan[i][0]["current_hash"] = groot_bscan[i+1][0].get('previous_hash')

    groot_bscan = sorted(groot_bscan, key=lambda k: k[0].get('timestamp'), reverse=True) # 기본값은 false로 오름차순 정렬(reverse=True 옵션으로 내림차순 정렬)

    return groot_bscan

def groot_scan(request):
    transactions = get_tx()
    blocks = get_block(5)

    # DB에 등록된 기술 및 블록에 쌓인 시간 조회
    technology = Enrollment.objects.filter(enroll_status=1)
    title = [] # 임치된 기술 갯수
    e_date = [] # 각 기술별 등록 날짜(그래프에 사용)
    for tech in technology :
        title.append(tech.title)

    for tx in transactions : 
        e_date.append(tx[0].get('transactions').get('timestamp'))

    # 첫 화면 그래프 출력을 위한 코드
    today = datetime.date.today()
    day_x = [today] # 일자(최근 10일)
    count_y = 0 # 일자별 tx 수         
    canvas = [] # 그래프를 그릴 최종 데이터
    x, y = [], [] # 배열 초기화
    for i in range(1,11) : # 9번 실행(배열에 10개 값 쌓이도록)
        day_x.append(today - datetime.timedelta(days=i))

    # 일자별 tx 건수 JSON 배열에 추가
    for i in range(0,10) :
        for j in range(0, len(e_date)) :
            if str(day_x[i]) == datetime.datetime.strftime(e_date[j], '%Y-%m-%d') : # 그래프에 출력하고자 하는 날짜와 임치일자가 같으면
                count_y = count_y + 1   
        canvas.append({day_x[i] : count_y})
        count_y = 0 # 데이터가 쌓였기 때문에 초기화    
    # print(canvas)
    
    for c in canvas :
        for key, val in c.items() :
            x.append(str(key)[5:]) # 시간 자르고 day까지만 추가
            y.append(val)
    #x.sort() #날짜 정렬
    x.reverse() # 날짜순 정렬
    y.reverse() # 값도 다시 정렬
    fig = plt.figure() # 판 제작
    plt.plot(x, y, 'wo-', mfc='#17354c') # white, o모양, -선, maker_face_color(구멍뚫기)
    # plt.grid(True) # 눈금표시
    fig.patch.set_facecolor('#17354c')
    fig.set_size_inches(7.5, 2.6)

    ax = fig.add_subplot(1,1,1)
    ax.set_yticks([0,4,8,12,16,20]) # y축 눈금지정
    ax.tick_params(color='white', labelcolor='white')
    ax.spines['top'].set_color('none')
    ax.spines['left'].set_color('white')
    ax.spines['bottom'].set_color('white')
    ax.spines['right'].set_color('none')
    fig.savefig(r'groot/static/groot_scan.png', facecolor=fig.get_facecolor(), transparent=True)
    
    return render(request, 'groot/groot_scan.html', {'number':title, 'transactions': transactions, 'blocks':blocks})

def groot_block(request):
    height = get_height()
    blocks = get_block(height)
    time = datetime.datetime.now()

    for block in blocks :
        b_timestamp = block[0].get('timestamp')
        b_diff = time - b_timestamp # 시간차이 구하기
        b_diff = str(b_diff)[:-7] # milisecond 제외한 값만 보내기
        block[0]["timestamp"] = b_diff # 값 update

    return render(request, 'groot/groot_block.html', {'blocks':blocks})

def groot_block_detail(request, height):
    m_height = get_height()
    m_height = int(m_height) - 1  # 현재 블록의 높이(0부터 시작하므로)
    block = [] # click 한 block 정보만 넣을 배열
    time = datetime.datetime.now()

    for i in range(height, height+2) :
        if i > m_height : # 블록 높이를 초과할 경우 chaincode에 접근하지 않음(에러나니까)
            break

        fabric = "http://210.107.78.147:8001/query_block/" + str(i)
        result = requests.get(fabric)
        block_parse = result.json()

        block_num = block_parse.get('info').get('block_number')
        previous_hash = block_parse.get('info').get('previous_hash')
        data_hash = block_parse.get('info').get('data_hash')
        transactions = block_parse.get('info').get('transactions')

        # 시간 변환
        timestamp = block_parse.get('data')[0]['Timestamp'][0:-5]
        timestamp = timestamp.split('T')
        timestamp = ' '.join(timestamp)
        timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        timestamp = timestamp + datetime.timedelta(hours=9)
        # 현재시간과의 차이 구하기
        t_diff = time - timestamp # 시간차이 구하기
        t_diff = str(t_diff)[:-7] # milisecond 제외한 값만 보내기

        tx = block_parse.get('data')[0].get("Transaction_ID")
        pre_block = int(block_num) - 1 # data 추가(이전블록 넘버)
        next_block = int(block_num) + 1 # data 추가(다음블록 넘버)
        block.append([{"block_number": block_num, "previous_hash": previous_hash, "data_hash": data_hash, "current_hash": None, "timestamp": timestamp,
                        "t_diff": t_diff, "transactions": transactions, "tx": tx, "pre_block": pre_block, "next_block": next_block}])

    if height == m_height : # 마지막 블록의 current_hash는 data_hash로 대체
        block[0][0]["current_hash"] = block[0][0].get('data_hash')
    else : # 아니면 다음 블록의 previous_hash 가져와서 대입
        block[0][0]["current_hash"] = block[1][0].get('previous_hash')

    # Hyperledger-Fabric에서 txid 별 data 얻어오기
    tx = block[0][0].get('tx')
    if tx == '' : # genesis 블록의 경우
        block_size = 'genesis block'
    else :
        fabric = "http://210.107.78.147:8001/query_tx/" + tx
        result = requests.get(fabric)
        parse = result.json()

        try :
            data = parse.get('data').get('value')
        except AttributeError : # 값이 없으면
            data = "null"

        block_size = str(sys.getsizeof(data)) + 'bytes' # bytes 크기로 블록 size 구하기

    return render(request, 'groot/groot_block_detail.html', {'height':height, 'blo':block[0], 'm_height':m_height, 'block_size':block_size})

def groot_transaction(request):
    transaction = get_tx()
    time = datetime.datetime.now()

    for tx in transaction:
        t_timestamp = tx[0].get('transactions').get('timestamp')
        t_diff = time - t_timestamp # 시간차이 구하기
        t_diff = str(t_diff)[:-7] # milisecond 제외한 값만 보내기
        # print(t_diff)
        tx[0]["transactions"]["timestamp"] = t_diff # 값 update

    return render(request, 'groot/groot_transaction.html', {'transactions':transaction})

def groot_transaction_detail(request, txid):
    time = datetime.datetime.now()

    # Hyperledger-Fabric에서 txid 별 data 얻어오기
    fabric = "http://210.107.78.147:8001/query_tx/" + txid
    result = requests.get(fabric)
    parse = result.json()

    block_number = parse.get('block_number')
    timestamp = parse.get('timestamp')[:-5]

    try :
        data = parse.get('data').get('value')
    except AttributeError : # 값이 없으면
        data = "null"

    # 시간 변환    
    timestamp = timestamp.split('T')
    timestamp = ' '.join(timestamp)
    timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    timestamp = timestamp + datetime.timedelta(hours=9)
    # 현재시간과의 차이 구하기
    t_diff = time - timestamp # 시간차이 구하기
    t_diff = str(t_diff)[:-7] # milisecond 제외한 값만 보내기

    return render(request, 'groot/groot_transaction_detail.html', {'txid':txid, 'block_number':block_number, 'timestamp':timestamp, 'data':data, 't_diff':t_diff})

@my_login_required
def read(request):
    try:
        request.session['otp']
    except KeyError:
        return redirect('/wrong')
    else:
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
    try:
        request.session['otp']
    except KeyError:
        return redirect('/wrong')
    else:
        user_id = request.session['user_id']
        enroll_infos = Enrollment.objects.all().filter(user_id=user_id, enroll_status=1)

        return render(request, 'groot/validate_intro.html', {'enroll_infos': enroll_infos})

@my_login_required
def validate_show(request, idx):
    try:
        request.session['otp']
    except KeyError:
        return redirect('/wrong')
    else:
        user_id = request.session['user_id']
        enroll_info = Enrollment.objects.get(enroll_idx=idx)
        file_info = File.objects.all().filter(enroll_idx=idx)
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
                with open(path + '\\' + upload_file.name, 'rb', encoding=None) as file: # 읽기모드로 파일 꺼내옴
                    textdata = file.read()

                hash = hashSHA(textdata).hexdigest()
                name = upload_file.name
                print(hash)
                template = get_template('groot/validate_show.html')
                os.remove(path + '\\' + upload_file.name) # 검증하고자하는 파일이 쌓일 필요는 없기 때문에 hash값만 뽑은 후 파일 삭제!!

                # Hyperledger-Fabric에서 데이터 받아오기
                #    0          1        2         3        4        5           6         7          8           9           10
                # Technology   Sort   Company   Com_num   Term   File_name   File_hash   Client   Cont_term   Enroll_date   Status
                fabric = "http://210.107.78.147:8001/get_cert_verify/" + enroll_info.title
                result = requests.get(fabric)

                parses = result.json() # JSON형식으로 parse(분석)
                method = 'post'
                for parse in parses:
                    txid = parse.get('TxId')
                    if txid == enroll_info.enroll_tx : # 파일등록시 쌓인 content 값 가져오기
                        content = parse.get('Value').get('content')

                try: # 블록에 접근해서 값 비교하기
                    if content[name] == hash : # 해쉬 같으면 원본 맞음
                        value = {'method':method, 'file_name': name, 'ck_val': 0, 'true_hash': content[name], 'val_hash': hash, 'enroll_idx': idx, 'enroll_info' : enroll_info, 'file_info':file_info}
                        return render(request, 'groot/validate_show.html', value)
                    else : # 해쉬 다르면 위변조 됨
                        value = {'method':method, 'file_name': name, 'ck_val': 1, 'true_hash': content[name], 'val_hash': hash, 'enroll_info' : enroll_info,'enroll_idx': idx, 'file_info':file_info}
                        return render(request, 'groot/validate_show.html', value)
                except KeyError : # KeyError는 없는 문서
                    value = {'method':method, 'file_name': name, 'ck_val': 2, 'enroll_idx': idx, 'file_info': file_info, 'enroll_info' : enroll_info,}
                    return render(request, 'groot/validate_show.html', value)
        else:
            method = 'get'
            return render(request, 'groot/validate_show.html',{'file_info':file_info,'enroll_info' : enroll_info, 'method':method })

def bye(request):
    user_id = request.session.get('user_id')
    userinfo = User.objects.get(user_id=user_id)
    enroll_infos = Enrollment.objects.all()
    contract_infos = Contract.objects.all()
    enroll_count = 0
    contract_is_value = 0

    for enroll_info in enroll_infos:
        if enroll_info.user.user_id == user_id and enroll_info.enroll_status == 1:
            enroll_count += 1

    for contract_info in contract_infos:
        if ((contract_info.enroll_idx.user.user_id == user_id and contract_info.status == 1) or (contract_info.user.user_id == user_id and contract_info.status == 1)):
            contract_is_value += 1
    
    if request.method == 'GET':
        return render(request, 'groot/bye.html', {'enroll_count':enroll_count, 'contract_is_value':contract_is_value, 'userinfo':userinfo})
    else:
        password = request.POST['pw1']

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
            enrollinfo.expire_status = 'impossible'
            enrollinfo.save()

        return redirect('mypage')

    else:
        create_date = datetime.date.today()
        form = ExpireForm()

    return render(request, 'groot/expire.html', {'edate':edate,'enrollinfo': enrollinfo,'form': form,'create_date':create_date})

def search_form(request):
    error = False
    user_id = request.session['user_id']
    contract_info = Contract.objects.all().filter(user_id=user_id)
    cont_lists = [] # 계약에 쓰일 리스트
    flag1 = {} # 계약 여부를 따질 변수

    if 'q' in request.GET:
        q = request.GET['q']
        if not q:
            error = True
        else:
            if 's_option' in request.GET:
                s_option = request.GET['s_option']
                if s_option == '1':
                    result = Enrollment.objects.filter(Q(title__icontains=q)).distinct().order_by('-enroll_date')
                    r_result = result.filter(agree_status=1)
                    for enroll_info in r_result:  # 계약 정보 관련
                        flag1[enroll_info.enroll_idx] = 2 #계약 신청 가능
                        for cont in contract_info:
                            if enroll_info.enroll_idx == cont.enroll_idx.enroll_idx: #계약이 되어있을때
                                if cont.status == 0:  # 계약 요청된 상태
                                    flag1[enroll_info.enroll_idx] = 0
                                    cont.status = "<button class='btn btn-outline-danger ck_button disabled' style='padding: 6px 3px 6px 3px;font-size:80%; border-color:rgb(238, 89, 89); width:96px;text-align: center;'>계약 요청중</button>"
                                else :  # 계약 완료인 상태
                                    flag1[enroll_info.enroll_idx] = 1
                                    cont.status = "<button class='btn btn-outline-danger_01 ck_button disabled' style='padding: 6px 3px 6px 3px;font-size:80%; border-color:#007bff; width:96px;text-align: center;'>계약중</button>"
                                cont_lists.append(cont)

                    return render(request, 'groot/search_result.html', {'r_result': r_result, 'query': q, 's_option':s_option,'cont_info': contract_info, 'cont_infos1':cont_lists, 'flag1':flag1,})
                elif s_option == '2' :
                    result = Enrollment.objects.filter(Q(summary__icontains=q)).distinct().order_by('-enroll_date')
                    r_result = result.filter(agree_status=1)
                    for enroll_info in r_result:  # 계약 정보 관련
                        flag1[enroll_info.enroll_idx] = 2 #계약 신청 가능
                        for cont in contract_info:
                            if enroll_info.enroll_idx == cont.enroll_idx.enroll_idx: #계약이 되어있을때
                                if cont.status == 0:  # 계약 요청된 상태
                                    flag1[enroll_info.enroll_idx] = 0
                                    cont.status = "<button class='btn btn-outline-danger ck_button disabled' style='padding: 6px 3px 6px 3px;font-size:80%; border-color:rgb(238, 89, 89); width:96px;text-align: center;'>계약 요청중</button>"
                                else :  # 계약 완료인 상태
                                    flag1[enroll_info.enroll_idx] = 1
                                    cont.status = "<button class='btn btn-outline-danger_01 ck_button disabled' style='padding: 6px 3px 6px 3px;font-size:80%; border-color:#007bff; width:96px;text-align: center;'>계약중</button>"
                                cont_lists.append(cont)

                    return render(request, 'groot/search_result.html', {'r_result': r_result, 'query': q, 's_option':s_option,'cont_info': contract_info, 'cont_infos1':cont_lists, 'flag1':flag1,})
                elif s_option == '3' :
                    result = Enrollment.objects.filter(Q(title__icontains=q) | Q(summary__icontains=q)).distinct().order_by('-enroll_date')
                    r_result = result.filter(agree_status=1)
                    for enroll_info in r_result:  # 계약 정보 관련
                        flag1[enroll_info.enroll_idx] = 2 #계약 신청 가능
                        for cont in contract_info:
                            if enroll_info.enroll_idx == cont.enroll_idx.enroll_idx: #계약이 되어있을때
                                if cont.status == 0:  # 계약 요청된 상태
                                    flag1[enroll_info.enroll_idx] = 0
                                    cont.status = "<button class='btn btn-outline-danger ck_button disabled' style='padding: 6px 3px 6px 3px;font-size:80%; border-color:rgb(238, 89, 89); width:96px;text-align: center;'>계약 요청중</button>"
                                else :  # 계약 완료인 상태
                                    flag1[enroll_info.enroll_idx] = 1
                                    cont.status = "<button class='btn btn-outline-danger_01 ck_button disabled' style='padding: 6px 3px 6px 3px;font-size:80%; border-color:#007bff; width:96px;text-align: center;'>계약중</button>"
                                cont_lists.append(cont)

                    return render(request, 'groot/search_result.html', {'r_result': r_result, 'query': q, 's_option':s_option,'cont_info': contract_info, 'cont_infos1':cont_lists, 'flag1':flag1,})

    return render(request, 'groot/search.html', {'error': error})

def upload(request):
    return render(request, 'groot/upload.html', {})

def application_list(request):

    user_id = request.session['user_id']
    enroll_infos = Enrollment.objects.all().filter(user=user_id).order_by('-c_date')
    extend_infos = Extend.objects.all()
    expire_infos = Expire.objects.all()
    now_date = datetime.datetime.now().date()
    file_list = File.objects.all()
    enroll_lists = []

    for enroll_info in enroll_infos:
        if enroll_info.agree_status == 0:
            enroll_info.agree_status = '비동의'
        else:
            enroll_info.agree_status = '동의'

        if enroll_info.end_date:
            enroll_info.end_date = enroll_info.end_date.date()

        if not enroll_info.enroll_tx:
            enroll_info.enroll_tx = '-'

        if not enroll_info.enroll_date:
            enroll_info.enroll_date = '-'

        if enroll_info.enroll_status == 0:
            enroll_info.enroll_status = "<div style='color:green'>대기중</div>"
        elif enroll_info.enroll_status == 1 and enroll_info.end_date > now_date :
            enroll_info.enroll_status = "<div style='color:blue'>승인</div>"
        elif enroll_info.enroll_status == 2:
            enroll_info.enroll_status = "<div style='color:red'>반려</div>"
        elif enroll_info.enroll_status == 1 and enroll_info.end_date < now_date:
            enroll_info.enroll_status = "<div style='color:red'>기간만료</div>"
        else:
            enroll_info.enroll_status = "<div style='color:red'>해지</div>"
        enroll_lists.append(enroll_info)

    return render(request, 'groot/application_list.html', {'file_list':file_list, 'expire_infos':expire_infos, 'extend_infos':extend_infos, 'enroll_infos':enroll_lists})

def request_list(request):
    user_id = request.session['user_id']
    extend_infos = Extend.objects.all()
    expire_infos = Expire.objects.all()
    contract_infos = Contract.objects.all()
    extend_lists = []
    expire_lists = []
    contract_lists = []

    for extend_info in extend_infos:
        status = ''
        if (extend_info.enroll_idx.user.user_id == user_id):
            if extend_info.status == 0:
                extend_info.status = "<td style='color:green;font-weight:500'>대기중</td>"
                extend_info.enroll_idx.end_date += datetime.timedelta(days=(365 * int(extend_info.term)))
            elif extend_info.status == 1:
                extend_info.status = "<td style='color:blue;font-weight:500'>승인</td>"
            else:
                extend_info.status = "<td style='color:red;font-weight:500'>반려</td>"
                extend_info.enroll_idx.end_date += datetime.timedelta(days=(365 * int(extend_info.term)))

            extend_lists.append(extend_info)

    for contract_info in contract_infos:
        status = ''
        if (contract_info.user.user_id == user_id):
            if contract_info.status == 0:
                contract_info.status = "<td style='color:green;font-weight:500'>대기중</td>"
            elif contract_info.status == 1:
                contract_info.status = "<td style='color:blue;font-weight:500'>승인</td>"
            else:
                contract_info.status = "<td style='color:red;font-weight:500'>반려</td>"
            contract_lists.append(contract_info)

    for expire_info in expire_infos:
        status = ''
        if expire_info.enroll_idx.user.user_id == user_id:
            if expire_info.status == 0:
                expire_info.status = "<td style='color:green;font-weight:500'>대기중</td>"
            elif expire_info.status == 1:
                expire_info.status = "<td style='color:blue;font-weight:500'>승인</td>"
            else:
                expire_info.status = "<td style='color:red;font-weight:500'>반려</td>"
            expire_lists.append(expire_info)


    return render(request, 'groot/request_list.html', {'contract_lists':contract_lists, 'expire_lists':expire_lists, 'status':status, 'extend_lists':extend_lists})

def contract_list(request):

    user_id = request.session['user_id']
    contract_infos = Contract.objects.all()
    contract_accepted = Contract.objects.all().filter(status=1)
    contract_lists = []
    now_date = datetime.datetime.now()
    for contract_info in contract_accepted:
        if contract_info.end_date > now_date:
            contract_info.status = "<td style='color:blue'>계약중</td>"
        else:
            contract_info.status = "<td style='color:red'>계약만료</td>"
        contract_info.accept_date = contract_info.accept_date.date()
        contract_info.end_date = contract_info.end_date.date()
        
        contract_lists.append(contract_info)


    return render(request, 'groot/contract_list.html', {'contract_lists':contract_lists, 'user_id':user_id, 'contract_infos':contract_infos})

def contract_list_detail(request, idx):

    contract_infos = Contract.objects.get(cont_idx=idx)
    enrolldate = contract_infos.enroll_idx.enroll_date.date()
    enddate = contract_infos.enroll_idx.end_date.date()
    cdate = contract_infos.c_date.date()
    enroll_idx = contract_infos.enroll_idx.enroll_idx
    enrollment_info = Enrollment.objects.get(enroll_idx=enroll_idx)

    if request.method == 'GET':
        return render(request, 'groot/contract_list_detail.html', {'cdate':cdate, 'enddate':enddate, 'enrolldate':enrolldate, 'contract_infos':contract_infos})
    else:
        if request.POST.get('yes'):
            contract_infos.status = 1
            contract_infos.accept_date = datetime.datetime.now()
            contract_infos.end_date = contract_infos.accept_date + datetime.timedelta(days=365 * contract_infos.term)

            # Hyperledger fabric 연결
            #     0          1        2         3        4        5       6          7            8          9
            # Technology   Sort   Company   Com_num   Term   Content   Client   Cont_term   Enroll_date   Status
            fabric = "http://210.107.78.147:8001/add_client/" + enrollment_info.title + "@" \
                     + contract_infos.user.user_id + "@" \
                     + str(contract_infos.term) + "@" + "4"
            f = requests.get(fabric)
            print(f.text)  # cmd 창에 보여질 값
            contract_infos.contract_tx = f.text[1:-1]
            contract_infos.save()

        else:
            contract_infos.refused_reason = request.POST['refused_reason']
            contract_infos.status = 2
            contract_infos.accept_date = datetime.datetime.now()
            contract_infos.save()
        return redirect('mypage')

@csrf_exempt
def otpmaker(request):
    if request.method == 'GET':
        user_id = request.session['user_id']
        return render(request, 'groot/mypage.html', {'user_id': user_id})
    else:
        user_id = request.session['user_id']
        user_info = User.objects.get(user_id=user_id)
        otp = pyotp.random_base32()
        key = b'PvyhpBY3ACtXhj_wm9ueKhFSYyKAz4ntMc3p6sKYvuI='
        cipher_suite = Fernet(key)
        ciphered_text = cipher_suite.encrypt(b"%s" % bytes(otp.encode('utf-8')))
        with open('otp/%s.bin' % user_id, 'wb') as file_object:
            file_object.write(ciphered_text)
        otpsave = User.objects.get(user_id=user_id)
        result_dict = {}

        if user_info.otp == None:
            # otpsave.otp = "Issued"
            # otpsave.save()
            data = pyotp.totp.TOTP(otp).provisioning_uri(user_id, issuer_name="Groot OTP App")
            validates = pyotp.totp.TOTP(otp).now()
            output = {"otp": otp, 'data': data, 'validates':validates}
            return JsonResponse(output)
        else:
            result_dict['result'] = 'Already Issued'
            return JsonResponse(result_dict)

def about_us(request):
    return render(request, 'groot/about_us.html', {})

def about_introduce(request):
    return render(request, 'groot/about_introduce.html', {})

def wrong(request):
    return render(request, 'groot/wrong.html', {})
