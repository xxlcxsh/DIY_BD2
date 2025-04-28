from django.http import HttpResponse
from django.shortcuts import render
def index(request):
    return render(request,'main/index.html')
def projects(request):
    return render(request,'main/projects.html')
def components(request):
    return render(request,'main/components.html')
def personal(request):
    return render(request,'main/personal.html')

