from django.shortcuts import render

# Create your views here.

def groot(request):
    return render(request, 'groot/main.html', {})