from django.http import HttpResponse
from django.shortcuts import render
def homepageview(request):
    return HttpResponse("Hello, world. You're at the polls page.")
def test(request):
    return render(request,'main/header.html')
