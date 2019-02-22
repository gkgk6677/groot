"""blockchain URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from groot.views import app_pdf, cont_pdf
from groot import views
# from groot.views import SearchFormView

urlpatterns = [
    path('', views.groot),
    path('login', views.login, name='login'),
    path('login_otp', views.login_otp, name='login_otp'),
    path('need_otp', views.need_otp, name="need_otp"),
    path('need_login', views.need_login, name="need_login"),
    path('mypage_otp', views.mypage_otp, name="mypage_otp"),
    path('otp_pwcheck', views.otp_pwcheck, name="otp_pwcheck"),
    path('join', views.join, name='join'),
    path('main', views.groot, name='main'),
    path('register', views.register, name='register'),
    path('application', views.application, name='application'),
    path('mypage', views.mypage, name='mypage'),
    path('list', views.list, name='list'),
    path('logout', views.logout, name='logout'),
    path('notice', views.notice, name='notice'),
    path('notice_write', views.notice_write, name='notice_write'),
    path('test', views.test, name='test'),
    path('issue/', views.issue, name='issue'),
    path('issue/show_app/<int:idx>', app_pdf.as_view()),
    path('issue/show_cont/<int:en_idx>-<int:cont_idx>', cont_pdf.as_view()),
    path('groot_scan/', views.groot_scan, name='groot_scan'),
    path('groot_scan/block/', views.groot_block, name='groot_block'),
    path('groot_scan/block/<int:height>', views.groot_block_detail, name='groot_block_detail'),
    path('groot_scan/transaction/', views.groot_transaction, name='groot_transaction'),
    path('groot_scan/transaction/<str:txid>', views.groot_transaction_detail, name='groot_transaction_detail'),
    path('read', views.read, name='read'),
    path('validate/', views.validate_intro, name='validate_intro'),
    path('validate/<int:idx>', views.validate_show, name='validate_show'),
    path('bye', views.bye, name='bye'),
    path('extend/<int:idx>', views.extend, name='extend'),
    path('search/insert/<int:idx>', views.insert, name='insert'),
    path('expire/<int:idx>', views.expire, name='expire'),
    path('upload', views.upload, name='upload'),
    path('wrong', views.wrong, name="wrong"),
    path('notice/(?P<pk>\d+)/$', views.notice_detail, name='notice_detail'),
    path('idcheck', views.idcheck, name='idcheck'),
    path('com_num_check', views.com_num_check, name='com_num_check'),
    path('change', views.change, name="change"),
    path('change_pw', views.change_pw, name="change_pw"),
    path('change_com', views.change_com, name="change_com"),
    # path('search', SearchFormView.as_view(), name='search'),
    # path('search/', views.search_list, name="search"),
    path('search/', views.search_form, name="search"),
    # path('search/', views.search_result, name="search"),

    path('login2', views.login2, name="login2"),
    path('login3', views.login3, name="login3"),
    path('application_list', views.application_list, name='application_list'),
    path('request_list', views.request_list, name='request_list'),
    path('contract_list', views.contract_list, name='contract_list'),
    path('contract_list/<int:idx>', views.contract_list_detail, name="contract_list_detail"),
    # path('login3', views.login3, name="login3"),
    path('download/<int:idx>', views.download, name='download'),
    path('otpmaker/', views.otpmaker, name='otpmaker'),
    path('about_us', views.about_us, name='about_us'),
    path('about_introduce', views.about_introduce, name='about_introduce'),
]

