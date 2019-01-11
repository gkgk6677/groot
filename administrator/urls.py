from django.urls import path
from administrator import views

urlpatterns = [
    path('index/', views.index, name="index"),
]