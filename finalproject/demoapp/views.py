from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from pymongo import MongoClient
from django.contrib.auth import logout
from django.contrib.auth.models import User, auth
import pymongo
from django.shortcuts import render, get_object_or_404
# from .models import Article
from bson import ObjectId
from django.http import Http404


# Create your views here.
def HomePage(request):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["database"]
    collection = db["ARTICLE"]
    data = collection.find()
    # for document in data:
    #     print(document)
    return render (request,'home.html',{ "data": data })

def Summary(request,slug):
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['database']
        collection = db['ARTICLE']
        
        if slug is not None:
            # print(slug)
            summarypage = collection.find_one({'slug': slug})
            
            # summarypage = get_object_or_404(collection, {'slug': slug})
            context = {'summarypage': summarypage}
            return render(request, 'summarizerpage.html', context)
            
           
    except Exception as e:
        return render(request, '404.html')
   

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
    # form = AuthenticationForm()
    return render (request,'login.html')



def LogoutPage(request):
    logout(request)
    return redirect('home')


    # client = MongoClient('mongodb://localhost:27017/')
    # db = client['database']
    # collection = db['ARTICLE']
    
    # if slug is not None:
    #     summarypage = get_object_or_404(collection, {'slug': slug})
    #     try:
    #         summarypage = collection.objects.get(slug=slug)
    #     except:
    #         raise Http404
    # context = {'summarypage': summarypage}
    # return render(request,'summarizerpage.html',context)
    
    # title = request.GET.get("title")
    # content = request.GET.get("content")
    # return render(request,'summarizerpage.html',{ "title":title, "content": content }) 



    