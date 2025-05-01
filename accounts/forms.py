from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from main.models import Users

class SignUpForm(UserCreationForm):
    sex_choices = [
        ('m', 'Мужской'),
        ('f', 'Женский'),
        ('o', 'Другой'),
    ]
    email = forms.EmailField(required=True)
    first_name=forms.CharField(required=True)
    second_name=forms.CharField(required=True)
    age=forms.IntegerField(required=True)
    sex=forms.ChoiceField(choices=sex_choices,required=True)

    class Meta:
        model = Users
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'second_name', 'age','sex')