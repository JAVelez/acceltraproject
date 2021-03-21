from django.urls import path

from . import views

app_name = ''
urlpatterns = [
    #  ex: /signup
    path('signup/', views.signup, name='vote'),
    #  ex: /student
    path('student/', views.StudentView.as_view(), name='student'),
]
