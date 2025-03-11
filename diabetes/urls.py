from django.urls import path
from . import views

urlpatterns = [
    path('prediction', views.prediction, name='prediction'),
    path('prediction/result/', views.result, name='result'),
    path('predictionshistory/', views.list_prediction, name='predictionshistory'),
]



