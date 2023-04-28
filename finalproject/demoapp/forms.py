from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import USER

class UserForm(forms.ModelForm):
    class Meta:
        model = USER
        fields = ['name', 'email', 'password', 'password_repeat']

class LoginForm(forms.Form):
    name = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)