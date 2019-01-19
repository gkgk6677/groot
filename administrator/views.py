from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import datetime, requests, json
from groot.models import *

# Create your views here.

def index(request):
    # if request.session == ['admin']:
        enroll_status = Enrollment.objects.all()
        contract_status = Contract.objects.all()
        extend_status = Extend.objects.all()
        update_status = Update.objects.all()
        expire_status = Expire.objects.all()

        count_enroll = 0
        count_cont = 0
        count_extend = 0
        count_update = 0
        count_expire = 0

        for val in enroll_status:
            if val.enroll_status == 0:
                count_enroll += 1
        for val in contract_status:
            if val.status == 0:
                count_cont += 1
        for val in extend_status:
            if val.status == 0:
                count_extend += 1
        for val in update_status:
            if val.status == 0:
                count_update += 1
        for val in expire_status:
            if val.status == 0:
                count_expire += 1

        return render(request, 'administrator/index.html', {'count_enroll':count_enroll, 'count_cont':count_cont, 'count_extend':count_extend, 'count_update':count_update, 'count_expire':count_expire})

def logout(request):
    del request.session['user_id']
    return redirect('main')

def blank(request):
    return render(request, 'administrator/blank.html', {})

def admin_application(request):   
    app_info = Enrollment.objects.all().filter(enroll_status=0)

    if request.method == 'GET':
        return render(request, 'administrator/admin-application.html', {'app_info':app_info})


def application_detail(request, idx):

    enrollment_info = Enrollment.objects.get(enroll_idx=idx)
    enrolldate = enrollment_info.c_date.date()

    if request.method == 'GET': 
        return render(request, 'administrator/application_detail.html', {'enrolldate':enrolldate, 'enrollment_info':enrollment_info})
    else:
        if request.POST.get('yes'):
            enrollment_info.enroll_status = 1
            enrollment_info.enroll_date = datetime.datetime.now()
            enrollment_info.end_date = datetime.datetime.now() + + datetime.timedelta(days=(365 * int(enrollment_info.term)))

            #     0          1        2         3        4        5       6          7            8          9
            # Technology   Sort   Company   Com_num   Term   Content   Client   Cont_term   Enroll_date   Status
            fabric = "http://210.107.78.150:8001/add_cont/" + enrollment_info.title + "@" + str(enrollment_info.sort_idx.sort_idx) + "@" \
                     + enrollment_info.user.com_name + "@" \
                     + str(enrollment_info.user.com_num) + "@" \
                     + str(enrollment_info.term) + "@" + "Content" + "@" + str(enrollment_info.enroll_date) + "@" + "1"
            f = requests.get(fabric)
            print(f.text)  # cmd 창에 보여질 값
            enrollment_info.enroll_tx = f.text[1:-1]
            enrollment_info.save()

            return redirect('index')
        elif request.POST.get('check'):
            return redirect('admin_application')
        else:
            enrollment_info.enroll_status = 2
            enrollment_info.enroll_date = datetime.datetime.now()
            enrollment_info.save()
            return redirect('index')

def admin_insert(request):

    insert_infos = Contract.objects.all().filter(status=0)

    return render(request, 'administrator/admin-insert.html', {'insert_infos':insert_infos})

def admin_extend(request):

    extend_info = Extend.objects.all().filter(status=0)

    return render(request, 'administrator/admin-extend.html', {'extend_info':extend_info})

def extend_detail(request, idx):

    extend_infos = Extend.objects.get(enroll_idx=idx, status=0)
    enroll_infos = Enrollment.objects.get(enroll_idx=idx)

    extend_date = extend_infos.c_date.date()
    enroll_enddate = enroll_infos.end_date.date()
    enroll_enrolldate = enroll_infos.enroll_date.date()


    if request.method == 'GET':
        return render(request, 'administrator/extend-detail.html', {'enroll_enrolldate':enroll_enrolldate, 'enroll_enddate':enroll_enddate, 'extend_date':extend_date, 'extend_infos':extend_infos, 'enroll_infos':enroll_infos})
    else:
        if request.POST.get('yes'):
            extend_infos.accept_date = datetime.datetime.now()
            extend_infos.status = 1
            extend_infos.save()
            enroll_infos.end_date += datetime.timedelta(days=(365 * int(extend_infos.term)))
            enroll_infos.save()
            return redirect('admin_extend')
        else:
            extend_infos.accept_date = datetime.datetime.now()
            extend_infos.status = 2
            extend_infos.save()
            return redirect('admin_extend')

            

def admin_update(request):

    update_infos = Update.objects.all().filter(status=0)

    return render(request, 'administrator/admin-update.html', {'update_infos':update_infos})

def admin_expire(request):

    expire_infos = Expire.objects.all().filter(status=0)

    return render(request, 'administrator/admin-expire.html', {'expire_infos':expire_infos})

def admin_log(request):
    return render(request, 'administrator/admin-log.html', {})

def admin_read(request):
    return render(request, 'administrator/admin-read.html', {})
