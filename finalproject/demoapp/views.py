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
import json
import pickle
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
import nltk
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
import numpy as np



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


#summarize using ml model
def text_preprocess(article):
    #tokenizing the text into words
    tokens = word_tokenize(article)
    
    #stop words and puntuations removal 
    stop_words = set(stopwords.words('english')+list(string.punctuation))
    #filter all the tokens not in stop words and convert into lower case
    filtered_tokens = [token.lower() for token in tokens if token.lower() not in stop_words]
    
    #lemmatize the filtered token
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(words) for words in filtered_tokens]
    
    #join the lemmatized tokens back into string
    text_preprocessed = ' '.join(lemmatized_tokens)
    
    return text_preprocessed

def summarize(article, n):
    # article=text_preprocess(article)
   #tfidfvectorizer obj: converting text data into matrix of word freq.
    vectorizer = TfidfVectorizer(stop_words='english')
    converted_metrics = vectorizer.fit_transform([article]) #fit the vectorizer to the text
    
    #aapplying svd to the matrix of word to extract hidden semantic structure.
    svd = TruncatedSVD(n_components=20)
    #term document matrix
    term_svd = svd.fit_transform(converted_metrics) 
    
    # Get most important sentences
    scores = np.sum(term_svd**2, axis=1)
    #sort ssentence according to thier score
    sentence_order = np.argsort(scores)[::-1]
    sentences = article.split('\n')
    # summary = '. '.join([sentences[i] for i in sentence_order[:n]])
    summary = '. '.join([sentences[i] + '.' for i in sentence_order[:n]])

    return summary

@csrf_protect
def get_summary(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        preprocess = text_preprocess(text)
        prediction = summarize(preprocess,4)
        print(preprocess)
        # print(prediction)
        context = {'text': text,'prediction':prediction}
        
    return render(request, 'summarizerpage.html',context)
