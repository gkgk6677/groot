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
    # path('index/insert/', views.admin_insert, name="admin_insert"),
    # path('index/insert/<int:idx>', views.insert_detail, name="insert_detail"),
    path('index/log/', views.admin_log, name="admin_log"),
    path('index/read/', views.admin_read, name="admin_read"),
    path('index/extend/', views.admin_extend, name="admin_extend"),
    path('index/extend/<int:idx>', views.extend_detail, name="extend_detail"),
    path('index/update/', views.admin_update, name="admin_update"),
    path('index/update/<int:idx>', views.update_detail, name="update_detail"),
    path('index/application/check/<int:idx>', views.check, name="check"),
    path('index/wrong', views.wrong, name="wrong"),
]