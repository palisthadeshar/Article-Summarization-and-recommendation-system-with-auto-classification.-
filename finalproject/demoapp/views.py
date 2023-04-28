from django.shortcuts import render
from .forms import UserForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate

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
            name = form.cleaned_data.get('name')
            password = form.cleaned_data.get('password_repeat')
            user = authenticate(name=name, password=password)
            if user is not None:
                login(request,user)
                return redirect('home')
            else:
                form.add_error(None, 'Invalid email or password.')
            
        else:
            form = UserForm()
    
    return render (request,'register.html', {'form':form})

def LoginPage(request):
    
    return render (request,'login.html')