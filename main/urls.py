from django.contrib import admin
from django.urls import path

from main import views
from main.views import purchase_subscription, subscription_success

urlpatterns = [path("",views.index,name="index"),
               path('projects/', views.projects_list, name='projects_list'),
               path('projects/add/', views.project_create, name='project_add'),
               path('projects/<int:pk>/', views.project_detail, name='project_detail'),
               path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
               path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
               path('components/', views.components_list, name='components_list'),
               path('components/add/', views.component_create, name='component_add'),
               path('components/<int:pk>/edit/', views.component_edit, name='component_edit'),
               path('components/<int:pk>/delete/', views.component_delete, name='component_delete'),
               path("profile/",views.profile,name="profile"),
               path('subscription/', purchase_subscription, name='purchase_subscription'),
               path('subscription/', subscription_success, name='purchase_subscription'),

]