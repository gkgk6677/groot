from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import datetime, requests, json
from groot.models import *
from sklearn.feature_extraction.text import TfidfVectorizer
from konlpy.tag import Kkma
from konlpy.utils import pprint

# Create your views here.

def index(request):
    if request.session['user_id'] == 'admin':
        if request.method == 'GET':
            enroll_status = Enrollment.objects.all()
            extend_status = Extend.objects.all()
            update_status = Update.objects.all()
            expire_status = Expire.objects.all()
            enroll_infos = Enrollment.objects.all().order_by('-c_date')[0:10]
            file_infos = File.objects.all()

            count_enroll = 0
            count_enrollments = 0
            count_cont = 0
            count_extend = 0
            count_expire = 0
            count_file = 0

            for val in enroll_status:
                if val.enroll_status == 0:
                    count_enroll += 1
                elif val.enroll_status == 1:
                    count_enrollments += 1
            for val in extend_status:
                if val.status == 0:
                    count_extend += 1
            for val in update_status:
                if val.status == 0:
                    count_update += 1
            for val in expire_status:
                if val.status == 0:
                    count_expire += 1
            for val in file_infos:
                count_file += 1
            

            return render(request, 'administrator/index.html',
                          {'count_enroll': count_enroll, 'count_cont': count_cont, 'count_extend': count_extend,
                           'enroll_infos': enroll_infos, 'count_expire': count_expire, 'count_file':count_file, 'count_enrollments':count_enrollments})
    else:
        return redirect('wrong')
        

def wrong(request):
    return render(request, 'administrator/wrong.html',{})

def logout(request):
    del request.session['user_id']
    return redirect('main')

def admin_application(request): 
    if request.session['user_id'] == 'admin':
        app_info = Enrollment.objects.all().filter(enroll_status=0).order_by('-c_date')

        if request.method == 'GET':
            return render(request, 'administrator/admin-application.html', {'app_info':app_info})
    else:
        return redirect('wrong')


def application_detail(request, idx):

    enrollment_info = Enrollment.objects.get(enroll_idx=idx)
    enrolldate = enrollment_info.c_date.date()

    if request.method == 'GET':
        return render(request, 'administrator/application_detail.html', {'enrolldate':enrolldate, 'enrollment_info':enrollment_info})
    else:
        if request.POST.get('check'):
            return redirect('/administrator/index/application/check/'+str(enrollment_info.enroll_idx))


def admin_extend(request):
    if request.session['user_id'] == 'admin':
        extend_info = Extend.objects.all().filter(status=0).order_by('-c_date')

        return render(request, 'administrator/admin-extend.html', {'extend_info':extend_info})
    else:
        return redirect('wrong')

def extend_detail(request, idx):

    if request.session['user_id'] == 'admin':
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
                enroll_infos.term += extend_infos.term
                enroll_infos.end_date += datetime.timedelta(days=(365 * int(extend_infos.term)))
                enroll_infos.save()

                #     0          1        2         3        4        5       6          7            8          9
                # Technology   Sort   Company   Com_num   Term   Content   Client   Cont_term   Enroll_date   Status
                fabric = "http://210.107.78.150:8001/change_term/" + enroll_infos.title + "@" \
                         + str(extend_infos.term) + "@" + "3"
                f = requests.get(fabric)
                print(f.text)  # cmd 창에 보여질 값
                # extend_infos.extend_tx = f.text[1:-1]
                # extend_infos.save()

                return redirect('index')
            else:
                extend_infos.accept_date = datetime.datetime.now()
                extend_infos.refused_reason = request.POST['refused_reason']
                extend_infos.status = 2
                extend_infos.save()
                return redirect('index')
    else:
        return redirect('wrong')

def admin_expire(request):

    if request.session['user_id'] == 'admin':
        expire_infos = Expire.objects.all().filter(status=0).order_by('-c_date')

        return render(request, 'administrator/admin-expire.html', {'expire_infos':expire_infos})
    else:
        return redirect('wrong')

def expire_detail(request, idx):

    if request.session['user_id'] == 'admin':
        expire_infos = Expire.objects.get(enroll_idx=idx, status=0)
        enroll_infos = Enrollment.objects.get(enroll_idx=idx)

        expire_date = expire_infos.c_date.date()
        enroll_enddate = enroll_infos.end_date.date()
        enroll_enrolldate = enroll_infos.enroll_date.date()
        if request.method == 'GET':
            return render(request, 'administrator/expire-detail.html', {'enroll_enrolldate':enroll_enrolldate, 'enroll_enddate':enroll_enddate, 'expire_date':expire_date, 'expire_infos':expire_infos, 'enroll_infos':enroll_infos})
        else:
            if request.POST.get('yes'):
                expire_infos.accept_date = datetime.datetime.now()
                expire_infos.status = 1
                expire_infos.save()
                enroll_infos.enroll_date = None
                enroll_infos.end_date = None
                enroll_infos.enroll_status = 3
                enroll_infos.save()
                return redirect('index')
            else:
                expire_infos.refused_reason = request.POST['refused_reason']
                expire_infos.accept_date = datetime.datetime.now()
                expire_infos.status = 2
                expire_infos.save()
                return redirect('index')
    else:
        return redirect('wrong')

def admin_read(request):

    if request.session['user_id'] == 'admin':
        enroll_infos = Enrollment.objects.all().filter(enroll_status=1).order_by('-c_date')

        return render(request, 'administrator/admin-read.html', {'enroll_infos':enroll_infos})
    else:
        return redirect('wrong')

def check(request, idx):

    if request.session['user_id'] == 'admin':
        old_summary_list = Enrollment.objects.all().filter(enroll_status=1)
        enrollment_info = Enrollment.objects.get(enroll_idx=idx)

        if request.method == 'GET':
            mydoclist = []
            titlelist = ['null']
            mydoclist += [enrollment_info.summary]

            for exist in old_summary_list:
                mydoclist += [str(exist.summary)]
                titlelist += [str(exist.title)]

            kkma = Kkma()
            doc_nouns_list = []

            for doc in mydoclist:
                nouns = kkma.nouns(doc)
                doc_nouns = ''

                for noun in nouns:
                    doc_nouns += noun + ' '

                doc_nouns_list.append(doc_nouns)

            tfidf_vectorizer = TfidfVectorizer(min_df=1)
            tfidf_matrix = tfidf_vectorizer.fit_transform(doc_nouns_list)

            document_distances =  (tfidf_matrix.T * tfidf_matrix)

            result = document_distances.toarray()

            one_row = result[0] # 유사도 분석 결과의 첫번째 배열 값 ex([1, 0.45, 0.75])

            request_count = 0
            test = []

            for val in range(1,len(one_row)):
                if (int(one_row[val] * 100) > 30 and int(one_row[val] * 100) != 100):
                    test.append([titlelist[val], mydoclist[val], (str(one_row[val] * 100)[0:5] + ' %')])
                    request_count += 1

            return render(request, 'administrator/check.html', {'test':test, 'request_count':request_count })
        else:
            if request.POST.get('yes'):
                enrollment_info.enroll_status = 1
                enrollment_info.enroll_date = datetime.datetime.now()
                enrollment_info.end_date = datetime.datetime.now() + + datetime.timedelta(
                    days=(365 * int(enrollment_info.term)))
                contents_list = File.objects.filter(enroll_idx=idx)
                file_name = ''
                file_hash = ''

                for content_list in contents_list :
                    file_name += content_list.file_name + ','
                    file_hash += content_list.file_hash + ','

                #     0          1        2         3        4        5       6          7            8          9
                # Technology   Sort   Company   Com_num   Term   Content   Client   Cont_term   Enroll_date   Status
                fabric = "http://210.107.78.150:8001/add_cont/" + enrollment_info.title + "@" \
                         + str(enrollment_info.sort_idx.sort_idx) + "@" \
                         + enrollment_info.user.com_name + "@" \
                         + str(enrollment_info.user.com_num) + "@" \
                         + str(enrollment_info.term) + "@" \
                         + file_name + "@" + file_hash + "@" \
                         + str(enrollment_info.enroll_date) + "@" + "1"
                f = requests.get(fabric)
                print(f.text)  # cmd 창에 보여질 값
                enrollment_info.enroll_tx = f.text[1:-1]
                enrollment_info.save()

                return redirect('index')
            else:
                enrollment_info.refused_reason = request.POST['refused_reason']
                enrollment_info.enroll_status = 2
                enrollment_info.enroll_date = datetime.datetime.now()
                enrollment_info.save()
                return redirect('index')
    else:
        return redirect('wrong')

def enrollments(request):

    if request.session['user_id'] == 'admin':
        enroll_infos = Enrollment.objects.all().filter(enroll_status=1).order_by('-c_date')

        return render(request, 'administrator/enrollments.html', {'enroll_infos':enroll_infos})
    else:
        return redirect('wrong')

def enrollments_detail(request, idx):

    if request.session['user_id'] == 'admin':
        enroll_infos = Enrollment.objects.get(enroll_idx=idx)
        enroll_enddate = enroll_infos.end_date.date()
        enroll_enrolldate = enroll_infos.enroll_date.date()

        return render(request, 'administrator/enrollments-detail.html', {'enroll_enrolldate':enroll_enrolldate, 'enroll_enddate':enroll_enddate, 'enroll_infos':enroll_infos})
    else:
        return redirect('wrong')

def admin_user(request):
    user_infos = User.objects.all().order_by('-c_date')
    
    return render(request, 'administrator/admin-user.html', {'user_infos':user_infos})