from django.urls import path
from .views import SignUpView
from main.views import custom_logout

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path('auth/logout/', custom_logout, name='custom_logout'),
]