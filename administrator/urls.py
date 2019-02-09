from django.urls import path
from administrator import views

urlpatterns = [
    path('index/', views.index, name="index"),
    path('index/logout/', views.logout, name='logout'),
    path('index/enrollments', views.enrollments, name='enrollments'),
    path('index/enrollments/<int:idx>', views.enrollments_detail, name="enrollments_detail"),
    path('index/application/', views.admin_application, name="admin_application"),
    path('index/application/<int:idx>', views.application_detail, name="application_detail"),
    path('index/expire/', views.admin_expire, name="admin_expire"),
    path('index/expire/<int:idx>', views.expire_detail, name="expire_detail"),
    path('index/read/', views.admin_read, name="admin_read"),
    path('index/extend/', views.admin_extend, name="admin_extend"),
    path('index/extend/<int:idx>', views.extend_detail, name="extend_detail"),
    path('index/application/check/<int:idx>', views.check, name="check"),
    path('index/wrong', views.wrong, name="wrong"),
    path('index/user', views.admin_user, name='admin_user'),
]