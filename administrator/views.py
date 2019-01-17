from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import datetime, requests, json
from groot.models import *

# Create your views here.

def index(request):
    enrollment_info = Enrollment.objects.all()
    contract_info = Contract.objects.all()
    count_enroll = 0
    count_cont = 0

    for val in enrollment_info:
        if val.status == 0:
            count_enroll += 1

    for val in contract_info:
        if val.user_id == 'eodahee':
            count_cont += 1


    return render(request, 'administrator/index.html', {'count_enroll':count_enroll, 'count_cont':count_cont})

def logout(request):
    del request.session['user_id']
    return redirect('main')

def blank(request):
    return render(request, 'administrator/blank.html', {})

def admin_application(request):

    app_info = Enrollment.objects.all().filter(status=1)

    return render(request, 'administrator/admin-application.html', {'app_info':app_info})

def application_detail(request, idx):

    enrollment_info = Enrollment.objects.get(enroll_idx=idx)


    return render(request, 'administrator/application_detail.html', {'enrollment_info':enrollment_info})

def admin_insert(request):
    return render(request, 'administrator/admin-insert.html', {})

def admin_extend(request):
    return render(request, 'administrator/admin-extend.html', {})

def admin_update(request):
    return render(request, 'administrator/admin-update.html', {})

def admin_expire(request):
    return render(request, 'administrator/admin-expire.html', {})

def admin_log(request):
    return render(request, 'administrator/admin-log.html', {})

def admin_read(request):
    return render(request, 'administrator/admin-read.html', {})
