from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import datetime, requests, json

# Create your views here.

def index(request):
    return render(request, 'administrator/index.html', {})