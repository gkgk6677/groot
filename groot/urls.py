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

from groot import views

urlpatterns = [
    path('', views.groot),
    path('login', views.login, name='login'),
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
    path('issue', views.issue, name='issue'),
    path('read', views.read, name='read'),
    path('validate', views.validate, name='validate'),
    path('news', views.news, name='news'),
    path('faq', views.faq, name='faq'),
    path('qna', views.qna, name='qna'),
    path('bye', views.bye, name='bye'),
    path('extend', views.extend, name='extend'),
    path('insert', views.insert, name='insert'),
    path('expire', views.expire, name='expire'),

    path('notice/(?P<pk>\d+)/$', views.notice_detail, name='notice_detail'),
]
]

