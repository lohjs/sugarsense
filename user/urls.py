from django.urls import path
from . import views


urlpatterns = [
    path('register', views.register, name='register'),
    path('signin', views.signin, name='signin'),
    path('signup', views.signup, name='signup'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('profiles', views.profiles, name='profiles'),
    path('change_password', views.change_password, name='change_password'),  
]