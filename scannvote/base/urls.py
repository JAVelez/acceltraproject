from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'home'
urlpatterns = [
    #  ex: home/signup
    path(r'signup/', views.signup, name='signup'),
    #  ex: home/student
    path(r'', views.home, name='home'),
    #  ex: home/login
    path(r'login/', views.login_student, name='login'),
    #  ex: home/logout
    path(r'logout/', views.logout_student, name='logout'),

]
