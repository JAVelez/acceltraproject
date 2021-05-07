from django.urls import path, include
from rest_framework import routers

from . import views

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'assemblies', views.AssemblyList)
router.register(r'motions', views.MotionList)
router.register(r'amendments', views.AmendmentList)


urlpatterns = [
    path('', include(router.urls)),
    #  ex: api/signup
    path('token/', views.token),
    #  ex: api/signup
    path('signup/', views.signup),
    #  ex: api/login
    path('login/', views.login_student),
    # ex: api/logout
    path('logout/', views.logout_student),
    # ex: /api/1
    path('assemblies/<int:pk>/', views.AssemblyDetail.as_view()),
    # ex: /api/motions/1
    path('motions/<int:pk>/', views.MotionDetail.as_view()),
    # ex: /api/amendments/1/vote
    path('motions/<int:pk>/vote', views.MotionDetailVote),
    # ex: /api/amendments/1
    path('amendments/<int:pk>/', views.AmendmentDetail.as_view()),
    # ex: /api/amendments/1/vote
    path('amendments/<int:pk>/vote', views.AmendmentDetailVote),

]