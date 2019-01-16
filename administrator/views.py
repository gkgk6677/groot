from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import datetime, requests, json
from groot import *

# Create your views here.

def index(request):
    return render(request, 'administrator/index.html', {})

def logout(request):
    del request.session['user_id']
    return redirect('main')

def blank(request):
    return render(request, 'administrator/blank.html', {})

def admin_application(request):
    return render(request, 'administrator/admin-application.html', {})

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
