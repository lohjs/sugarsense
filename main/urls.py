from django.urls import path,path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('ourvalues', views.ourvalues, name='ourvalues'),
    path('leadership', views.leadership, name='leadership'),
    path('careers', views.careers, name='careers'),
    path('research', views.research, name='research'),
    path('factors', views.factors, name='factors'),
    path('diet', views.diet, name='diet'),
    path('food', views.food, name='food'),
    path('chocolate', views.chocolate, name='chocolate'),
    path('treatment', views.treatment, name='treatment'),
    path('weightloss', views.weightloss, name='weightloss'),
    path('careersselection', views.careersselection, name='careersselection'),
    path('job-application', views.job_application, name='job_application'),
    path('diabeteseducator', views.diabeteseducator, name='diabeteseducator'),
    path('nutritionist', views.nutritionist, name='nutritionist'),
    path('fullstackdeveloper', views.fullstackdeveloper, name='fullstackdeveloper'),
    path('datascientist', views.datascientist, name='datascientist'),
    path('customersupportspecialist', views.customersupportspecialist, name='customersupportspecialist'),
    path('healthcareadministrator', views.healthcareadministrator, name='healthcareadministrator'),
    path('appointment', views.appointment, name='appointment'),
    path('contactus', views.contactus, name='contactus'),
    path('careers/<str:career_type>', views.process_career_application, name='career_application'),
    
]