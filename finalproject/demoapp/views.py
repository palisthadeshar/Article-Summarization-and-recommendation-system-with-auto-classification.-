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
from num2words import num2words
import re
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
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
import tensorflow as tf
from keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences



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
            # summarypage = get_object_or_404(collection, {'slug': slug})
            context = {'summarypage': summarypage,'id':object_id}
            return render(request, 'summarizerpage.html', context)            
    except Exception as e:
        return render(request, '404.html')
    

# def activateEmail(request,user,to_email):
#     mail_subject = 'Activate your account.'
#     message = render_to_string('activate_account.html', {
#                                     'user': user,
#                                     'domain': get_current_site(request).domain,
#                                     'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#                                     'token': account_activation_token.make_token(user),
#                                     'protocol':'https' if request.is_secure() else 'http'
#                                 })
#     email = EmailMessage(
#                         mail_subject, message, to=[to_email]
#             )
#     if email.send():

#         messages.success(request,f'Dear {user}, please go to your {to_email} inbox and activate your account.')
#     else:
#         messages.success(request,f'Problem sending email {to_email}, check your email if is it correct.')


# def activate(request,uidb64,token):
#     return redirect('home')
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
                                messages.info(request,'Email exists.')
                                raise DatabaseError('Email already exists')
                                # return redirect('signup')
                                    
                            else:
                                user = User.objects.create_user(username=name, email=email,password=password)
                                # user.is_active=False
                                
                                user.save()
                              
                                
                                # activateEmail(request,user,email)
                         
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
    article = article.replace('—', ' ')
    tokens = word_tokenize(article)
    # for i in range(len(tokens)):
    #     if tokens[i].isdigit():
    #         tokens[i] = num2words(tokens[i])
    text_preprocessed = ' '.join(tokens)
    return text_preprocessed

def summarize(article, n):
    sentences = article.split('. ')
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(sentences)
    svd = TruncatedSVD(n_components=20)
    X_lsa = svd.fit_transform(X)
    scores = np.sum(X_lsa**2, axis=1)
    sentence_order = np.argsort(scores)[::-1]
    summary = '. '.join([sentences[i] for i in sentence_order[:n]]) +'.'

    return summary

def preprocess_text(text):
    # Remove special characters and digits
    text = re.sub('[^a-zA-Z]', ' ', text)
    # Convert to lowercase
    text = text.lower()
    # Split into words
    words = text.split()
    # Join the words
    preprocessed_text = ' '.join(words)
    return preprocessed_text



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
        current_document = collection.find_one({'_id': ObjectId(id)})
        title=current_document['Title']
        content=current_document['Content']
        rnn_text=title+content[:3]
        #summarize
        preprocess = text_preprocess(text)
        prediction = summarize(preprocess,5)
        #classify
        pickled_model = pickle.load(open('./demoapp/ML_models/model.pkl', 'rb'))
        pickled_vectorizer = pickle.load(open('./demoapp/ML_models/vectorizer.pkl', 'rb'))
        classify_text = pickled_vectorizer.transform([title]).toarray()
        result=pickled_model.predict(classify_text)
        arr = result
        classify = arr[0].strip()
        #using lstm
        rnn_model = tf.keras.models.load_model('./demoapp/ML_models/model.hdf5')
        rnn_model.load_weights('./demoapp/ML_models/modelweight.h5')
        pickled_token = pickle.load(open('./demoapp/ML_models/token.pkl', 'rb'))
        labels = ['Business News', 'Sports News', 'World News', 'Science-Technology News']
        test_seq = pad_sequences(pickled_token.texts_to_sequences(rnn_text), maxlen=177)
        test_preds = [labels[np.argmax(i)] for i in rnn_model.predict(test_seq)]
        for  label in zip( test_preds):
            category_rnn=label
            category_rnn = category_rnn[0].strip()


        # recommend
        similarity_score=sim_score(contents)
        index = ids.index(id)
        scores = list(enumerate(similarity_score[index]))
        scores_sorted = sorted(scores, key=lambda x: x[1], reverse=True)
        num_recommendations=5
        recommended_ids = [ids[score[0]] for score in scores_sorted[1:num_recommendations+1]]
        recommended_articles = []
        for recommended_id in recommended_ids:
            recommended_article = collection.find_one({'_id': ObjectId(recommended_id)})
            recommended_articles.append(recommended_article)

        context = {'text': text,'prediction':prediction,'recommendation':recommended_articles,'title':title,'classify':classify,'category_rnn':category_rnn}
      
        
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
            prediction = summarize(preprocess,8)
            # pickled_model = pickle.load(open('./demoapp/ML_models/model.pkl', 'rb'))
            # pickled_vectorizer = pickle.load(open('./demoapp/ML_models/vectorizer.pkl', 'rb'))
            # classify_text = pickled_vectorizer.transform([text]).toarray()
            # result=pickled_model.predict(classify_text)
            # arr = result
            # classify = arr[0].strip()
            
            # print(preprocess)
            # print(prediction)
            context = {'text': text,'prediction':prediction}
            return render(request, 'summarizerpage_own.html',context)
    return render(request, 'summarizerpage_own.html')

#logout
def LogoutPage(request):
    logout(request)
    return redirect('home')
