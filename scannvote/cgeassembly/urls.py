from django.urls import path

from . import views

app_name = 'cgeassembly'
urlpatterns = [
    # ex: /cgeassembly/
    path('', views.AssemblyIndexView.as_view(), name='assemblyindex'),
    # ex: /cgeassembly/1
    path('<int:pk>/', views.AssemblyDetailView.as_view(), name='assemblydetail'),

    # # ex: /cgeassembly/
    # path('', views.MotionIndexView.as_view(), name='motionindex'),

    # ex: /assembly/cgeassembly/5/
    path('assembly/<int:pk>/', views.MotionDetailView.as_view(), name='motiondetail'),
    # ex: /assembly/cgeassembly/5/results/
    path('assembly/<int:pk>/results/', views.MotionResultsView.as_view(), name='motionresults'),
    # ex: /assembly/cgeassembly/5/vote/
    path('assembly/<int:motion_id>/vote/', views.vote, name='vote'),
]