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

            return render(request, 'administrator/index.html',
                          {'count_enroll': count_enroll, 'count_cont': count_cont, 'count_extend': count_extend,
                           'count_update': count_update, 'count_expire': count_expire})
    else:
        return redirect('wrong')
        

def wrong(request):
    return render(request, 'administrator/wrong.html',{})

def logout(request):
    del request.session['user_id']
    return redirect('main')

def admin_application(request): 
    if request.session['user_id'] == 'admin':
        app_info = Enrollment.objects.all().filter(enroll_status=0)

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


# def admin_insert(request):

#     insert_infos = Contract.objects.all().filter(status=0)

#     return render(request, 'administrator/admin-insert.html', {'insert_infos':insert_infos})

# def insert_detail(request, idx):

#     insert_infos = Contract.objects.get(enroll_idx=idx, status=0)
#     enroll_infos = Enrollment.objects.get(enroll_idx=idx) # 해당 임치물에 대한 정보(개발자 기업 idx)

#     insert_date = insert_infos.c_date.date()
#     enroll_enddate = enroll_infos.end_date.date()
#     enroll_enrolldate = enroll_infos.enroll_date.date()

#     if request.method == 'GET':
#         return render(request, 'administrator/insert-detail.html', {'insert_infos':insert_infos, 'enroll_infos':enroll_infos, 'insert_date':insert_date, 'enroll_enddate':enroll_enddate, 'enroll_enrolldate':enroll_enrolldate})


def admin_extend(request):
    if request.session['user_id'] == 'admin':
        extend_info = Extend.objects.all().filter(status=0)

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
                return redirect('admin_extend')
            else:
                extend_infos.accept_date = datetime.datetime.now()
                extend_infos.status = 2
                extend_infos.save()
                return redirect('admin_extend')
    else:
        return redirect('wrong')

def admin_update(request):
    if request.session['user_id'] == 'admin':
        update_infos = Update.objects.all().filter(status=0)

        return render(request, 'administrator/admin-update.html', {'update_infos':update_infos})
    else:
        return redirect('wrong')

def update_detail(request, idx):

    if request.session['user_id'] == 'admin':
        update_infos = Update.objects.get(enroll_idx=idx, status=0)
        enroll_infos = Enrollment.objects.get(enroll_idx=idx)
        update_date = update_infos.c_date.date()
        enroll_enddate = enroll_infos.end_date.date()
        enroll_enrolldate = enroll_infos.enroll_date.date()

        if request.method == 'GET':
            return render(request, 'administrator/update-detail.html', {'enroll_enrolldate':enroll_enrolldate, 'enroll_enddate':enroll_enddate, 'expire_date':expire_date, 'update_infos':update_infos, 'enroll_infos':enroll_infos})
        else:
            if request.POST.get('yes'):
                update_infos.status = 1
                update_infos.accept_date = datetime.datetime.now()
                update_infos.save()

            else:
                update_infos.status = 2
                update_infos.accept_date = datetime.datetime.now()
                update_infos.save()
    else:
        return redirect('wrong')


def admin_expire(request):

    if request.session['user_id'] == 'admin':
        expire_infos = Expire.objects.all().filter(status=0)

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
                expire_infos.accept_date = datetime.datetime.now()
                expire_infos.status = 2
                expire_infos.save()
                return redirect('index')
    else:
        return redirect('wrong')


def admin_log(request):

    if request.session['user_id'] == 'admin':
        return render(request, 'administrator/admin-log.html', {})
    else:
        return redirect('wrong')

def admin_read(request):

    if request.session['user_id'] == 'admin':
        return render(request, 'administrator/admin-read.html', {})
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

            document_distances =  (tfidf_matrix * tfidf_matrix.T)

            result = document_distances.toarray()

            one_row = result[0] # 유사도 분석 결과의 첫번째 배열 값 ex([1, 0.45, 0.75])

            request_count = 0
            result = []

            for val in range(1,len(one_row)):
                if (int(one_row[val] * 100) > 30 and int(one_row[val] * 100) != 100):
                    result.append({titlelist[val] : mydoclist[val]})
                    request_count += 1

            return render(request, 'administrator/check.html', {'result':result, 'request_count':request_count, 'one_row':one_row})
        else:
            if request.POST.get('yes'):
                enrollment_info.enroll_status = 1
                enrollment_info.enroll_date = datetime.datetime.now()
                enrollment_info.end_date = datetime.datetime.now() + + datetime.timedelta(
                    days=(365 * int(enrollment_info.term)))
                contents_list = File.objects.filter(enroll_idx=idx)
                content = ''

                for content_list in contents_list :
                    content += content_list.mid + ','

                #     0          1        2         3        4        5       6          7            8          9
                # Technology   Sort   Company   Com_num   Term   Content   Client   Cont_term   Enroll_date   Status
                fabric = "http://210.107.78.150:8001/add_cont/" + enrollment_info.title + "@" \
                         + str(enrollment_info.sort_idx.sort_idx) + "@" \
                         + enrollment_info.user.com_name + "@" \
                         + str(enrollment_info.user.com_num) + "@" \
                         + str(enrollment_info.term) + "@" + content + "@" \
                         + str(enrollment_info.enroll_date) + "@" + "1"
                f = requests.get(fabric)
                print(f.text)  # cmd 창에 보여질 값
                enrollment_info.enroll_tx = f.text[1:-1]
                enrollment_info.save()

                return redirect('index')
            else:
                enrollment_info.enroll_status = 2
                enrollment_info.enroll_date = datetime.datetime.now()
                enrollment_info.save()
                return redirect('index')
    else:
        return redirect('wrong')

def enrollments(request):

    if request.session['user_id'] == 'admin':
        enroll_infos = Enrollment.objects.all().filter(enroll_status=1)

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