from django.contrib import admin
from django.urls import path
from .views import homepageview,test

urlpatterns = [path("", homepageview, name="home"),
               path('test',test),

]