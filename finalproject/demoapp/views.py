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
from bson import ObjectId
from django.http import Http404
from django.db import DatabaseError
import json
from django.http import JsonResponse
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
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity



# Create your views here.
#home page
def HomePage(request):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["database"]
    collection = db["ARTICLE"]
    data = collection.find()
   

    return render (request,'home.html',{ "data": data })


def sim_score(preprocessed_text):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(preprocessed_text)
    similarity_score = cosine_similarity(tfidf_matrix)
    return similarity_score


#summarize the exisiting content
def Summary(request,slug):
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['database']
        collection = db['ARTICLE']
        # articles = list(collection.find())
        if slug is not None:
            # print(slug)
            summarypage = collection.find_one({'slug': slug})
            object_id = str(summarypage['_id'])
            content=summarypage['Content']
      
            # summarypage = get_object_or_404(collection, {'slug': slug})
            context = {'summarypage': summarypage,'id':object_id}
            return render(request, 'summarizerpage.html', context)            
    except Exception as e:
        return render(request, '404.html')


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

#summarize using ml model
def text_preprocess(article):
    #tokenizing the text into words
    tokens = word_tokenize(article)
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(words) for words in tokens]
    #join the lemmatized tokens back into string
    text_preprocessed = ' '.join(lemmatized_tokens)
    return text_preprocessed

def summarize(article, n):
    # Convert article to a list of sentences
    sentences = article.split('. ')
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(sentences)
    svd = TruncatedSVD(n_components=20)
    X_lsa = svd.fit_transform(X)
    # Get the most important sentences
    scores = np.sum(X_lsa**2, axis=1)
    sentence_order = np.argsort(scores)[::-1]
    # sentence_order = np.argsort(scores)
    # reverse_order = np.flipud(sentence_order)
    summary = '. '.join([sentences[i] for i in sentence_order[:n]])

    return summary




@csrf_protect
def get_summary(request):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['database']
    collection = db['ARTICLE']
    articles = list(collection.find())
    contents = [article['Content'] for article in articles]
    ids = [str(article['_id']) for article in articles]
    if request.method == 'POST':
        text = request.POST.get('text')
        id = request.POST.get('id')  
        preprocess = text_preprocess(text)
        prediction = summarize(preprocess,5)
        similarity_score=sim_score(contents)
        # print(similarity_score)
        index = ids.index(id)
        scores = list(enumerate(similarity_score[index]))
        scores_sorted = sorted(scores, key=lambda x: x[1], reverse=True)
        num_recommendations=5
        recommended_ids = [ids[score[0]] for score in scores_sorted[1:num_recommendations+1]]
        recommended_articles = []
        for recommended_id in recommended_ids:
            recommended_article = collection.find_one({'_id': ObjectId(recommended_id)})
            recommended_articles.append(recommended_article)

        context = {'text': text,'prediction':prediction,'recommendation':recommended_articles}
      
        
    return render(request, 'summarizerpage.html',context)



#to summarize own article
@csrf_protect
def SummarizeOwn(request):
    if not request.user.is_authenticated:
        return redirect('login')    
    else:
        if request.method == 'POST':
            text = request.POST.get('file_text')
            preprocess = text_preprocess(text)
            prediction = summarize(preprocess,10)
            
            # print(preprocess)
            # print(prediction)
            context = {'text': text,'prediction':prediction}
            return render(request, 'summarizerpage_own.html',context)
    return render(request, 'summarizerpage_own.html')

#logout
def LogoutPage(request):
    logout(request)
    return redirect('home')
