from django.shortcuts import render
from .forms import NewUserForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from pymongo import MongoClient
from django.contrib.auth import logout
from django.contrib.auth.models import User, auth
from .models import *

# Create your views here.
def HomePage(request):
    return render (request,'home.html')

def SignupPage(request):
      
    if request.method == 'POST':
        name = request.POST['username']
        email =  request.POST['email']
        password = request.POST['password']
        password_repeat = request.POST['password_repeat']

        if password==password_repeat:
            user = User.objects.create_user(username=name, email=email,password=password)
            user.save()
            #print('user created')
            return redirect('login')
        else:
            print('password doenot match')
    else:
        return render(request,'register.html')
        

    
def LoginPage(request):
    
    if request.method == 'POST':
        name = request.POST['name']
        password = request.POST['password']

        user = auth.authenticate(username=name, password=password)
        if user is not None :
            
            # print(authenticated_user)
           
            auth.login(request, user)
            messages.success(request,f'welcome {name}!')
            return redirect('home')
        else:
            messages.info(request,'Account doesnot exists. Please create an account.')
            return redirect('login')
    form = AuthenticationForm()
    return render (request,'login.html')



def LogoutPage(request):
    logout(request)
    return redirect('home')