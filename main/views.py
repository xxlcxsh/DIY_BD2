from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
def index(request):
    return render(request,'main/index.html')
@login_required
def projects(request):
    return render(request,'main/projects.html')
@login_required
def components(request):
    return render(request,'main/components.html')
@login_required
def personal(request):
    return render(request,'main/personal.html')

