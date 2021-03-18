from django.urls import path

from . import views

app_name = 'cgeassembly'
urlpatterns = [
    # ex: /cgeassembly/
    path('', views.IndexView.as_view(), name='index'),
    # ex: /cgeassembly/5/
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # ex: /cgeassembly/5/results/
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # ex: /cgeassembly/5/vote/
    path('<int:motion_id>/vote/', views.vote, name='vote'),
    #  ex: /cgeassembly/signup
    path('signup/', views.signup, name='vote'),
    #  ex: /cgeassembly/student
    path('student/', views.StudentView.as_view(), name='student'),
]