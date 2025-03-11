from django.urls import path
from . import views

urlpatterns = [
    path('recommendation', views.recommendation, name='recommendation'),
    path('recommendation_result', views.recommendation_result, name='recommendation_result'),
    path('recommendation_history', views.recommendation_history, name='recommendation_history'),
]