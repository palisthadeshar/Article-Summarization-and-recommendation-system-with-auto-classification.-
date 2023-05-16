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
from django.db import DatabaseError



# Create your views here.
#home page
def HomePage(request):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["database"]
    collection = db["ARTICLE"]
    data = collection.find()
    # for document in data:
    #     print(document)
    return render (request,'home.html',{ "data": data })


#summarize the exisiting content
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



#to summarize own article
def SummarizeOwn(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
        
    else:
        return render(request, 'summarizerpage_own.html')


#registration page
# database error solved!!! error msg is not displaying . Need to be resolved!!!!!!!
#email confirmation is yet to be done!!!
def SignupPage(request):
      
    if request.method == 'POST':
        name = request.POST['username']
        email =  request.POST['email']
        password = request.POST['password']
        password_repeat = request.POST['password_repeat']
       

        if (name == ' ' or email == ' ' or password == ' ' or password_repeat == ''):
            messages.info(request,'Input fields cannot be empty')
            return redirect('signup')
        else:
          
                    # if any field is not null goes here
                  
                    if password == password_repeat:  
                        try:

                            if User.objects.filter(username=name).exists(): 
                                messages.info(request,'User name exists.')
                                raise DatabaseError('Username already exists')   
                                # return redirect('signup')
                            
                            elif User.objects.filter(email=email).exists():
                                raise DatabaseError('Email already exists')
                                # return redirect('signup')
                                    
                            else:
                                user = User.objects.create_user(username=name, email=email,password=password)
                                user.save()
                                messages.info(request,'User Created sucessfully.')
                                return redirect('login')
                        except DatabaseError as msg:
                            messages.info(request,msg)
                            return redirect('signup')
                    else:
                                
                        messages.info(request,'Password doesnot matches.')
                        return redirect('signup')
            

            
    else:
        return render(request,'register.html')
        
        # print(User)
    #     try:
            
    #         if password == password_repeat:
    #             msg=""
    #             try:
    #                 # if any field is not null goes here
    #                 if (name == ' ' or email == ' ' or password == ' ' or password_repeat == ''):
                        
    #                     if User.objects.filter(username=name).exists():
    #                         messages.info(request,'User name already taken')
                            
    #                         return redirect('signup')
    #                     elif User.objects.filter(email=email).exists():
    #                         messages.info(request,'Email already taken')
    #                         return redirect('signup')
                            
    #                     else:
    #                         user = User.objects.create_user(username=name, email=email,password=password)
    #                         user.save()
    #                         messages.info(request,'User Created sucessfully.')
    #                         return redirect('login')
    #                 else:
    #                      print('i am here')
    #                      messages.info(request,'Input fields cannot be empty.')
    #                      return redirect('signup')
    #             except DatabaseError as msg:
    #                 messages.info(request, msg)
    #                 return redirect('signup')
    #         else:
                
    #             messages.info(request,'Password doesnot.')
    #             return redirect('signup')
                
    #     except ValueError:
    #         messages.info(request, 'Something went wrong. Please register again.')
    #         return redirect('signup')
    # else:
    #     return render(request,'register.html')
        


#login page
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


#logout
def LogoutPage(request):
    logout(request)
    return redirect('home')






    