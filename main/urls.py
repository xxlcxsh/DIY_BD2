from django.contrib import admin
from django.urls import path

from main import views

urlpatterns = [path("",views.index,name="index"),
               path("projects",views.projects,name="projects"),
               path("components",views.components,name="components"),
               path("personal",views.personal,name="personal"),
]