"""finalproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from demoapp import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.HomePage,name='home'),
    path('signup/',views.SignupPage, name='signup'),
    path('login/',views.LoginPage,name='login'),
    path('home/',views.LogoutPage,name='logout'),
    #displays the content ffrom home page
    path('summarypage/<slug:slug>/',views.Summary,name='summarypage'),
    #summarizes uploaded 
    path('summarypageown/',views.SummarizeOwn,name='summarypageown'), 
    #summarizes existing
    path('summary/',views.get_summary,name='summary'),
   
]
