from django.shortcuts import render
from .forms import UserForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
import pymongo
from pymongo import MongoClient

# Create your views here.
def HomePage(request):
    return render (request,'home.html')

def SignupPage(request):
     
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            password_repeat = form.cleaned_data.get('password_repeat')
            user.save()
            messages.success(request, 'You have singed up successfully.')
            # name = form.cleaned_data.get('name')
            # password = form.cleaned_data.get('password')
            # user = authenticate(name=name, password=password)
            # if user is not None:
            #     login(request,user)
            #     return redirect('home')
            # else:
            #     form.add_error(None, 'Invalid username or password.')
            
        else:
            form = UserForm()
    
    # return render (request,'register.html', {'form':form})
    return render (request,'register.html')

def LoginPage(request):
    if request.method == 'POST':
        name = request.POST['name']
        password = request.POST['password']

        client = MongoClient('mongodb://localhost:27017/')
        db = client['database']
        users = db['USER']

        user = users.find({'name': name, 'password': password})
        print(user)
        if user is not None :
            # login(request,user)
            messages.success(request,f'welcome {name}!')
            return redirect('home')
        else:
            messages.info(request,'Account doesnot exists. Please create an account.')
            return redirect('login')
    form = AuthenticationForm()
    return render (request,'login.html')