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
        if val.status == 0:
            count_cont += 1


    return render(request, 'administrator/index.html', {'count_enroll':count_enroll, 'count_cont':count_cont})

def logout(request):
    del request.session['user_id']
    return redirect('main')

def blank(request):
    return render(request, 'administrator/blank.html', {})

def admin_application(request):   
    app_info = Enrollment.objects.all().filter(status=0)

    if request.method == 'GET':
        return render(request, 'administrator/admin-application.html', {'app_info':app_info})


def application_detail(request, idx):

    enrollment_info = Enrollment.objects.get(enroll_idx=idx)
    if request.method == 'GET': 
        return render(request, 'administrator/application_detail.html', {'enrollment_info':enrollment_info})
    else:
        if request.POST.get('yes'):
            enrollment_info.status = 1
            enrollment_info.enroll_date = datetime.datetime.now()
            enrollment_info.end_date = datetime.datetime.now() + + datetime.timedelta(days=(365 * int(enrollment_info.term)))
            enrollment_info.save()

            #     0          1        2         3        4        5       6          7            8          9
            # Technology   Sort   Company   Com_num   Term   Content   Client   Cont_term   Enroll_date   Status
            fabric = "http://210.107.78.150:8001/add_cont/" + enrollment_info.title + "@" + str(enrollment_info.sort_idx.sort_idx) + "@" \
                     + enrollment_info.user.com_name + "@" \
                     + str(enrollment_info.user.com_num) + "@" \
                     + str(enrollment_info.term) + "@" + "Content" + "@" + str(enrollment_info.enroll_date) + "@" + "1"
            f = requests.get(fabric)
            print(f.text)  # cmd 창에 보여질 값

            return redirect('index')
        else:
            enrollment_info.status = 2
            enrollment_info.enroll_date = datetime.datetime.now()
            enrollment_info.save()
            return redirect('index')

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
