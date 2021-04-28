"""scannvote URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include
import base.views as views

admin.site.site_header = "Scan-N-Vote"
admin.site.site_title = "Scan-N-Vote"
admin.site.index_title = "Administrative Side"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cgeassembly/', include('cgeassembly.urls')),
    #  ex: /signup
    path(r'signup/', views.signup, name='signup'),
    #  ex: /
    path(r'', views.home, name='home'),
    #  ex: /login
    path(r'login/', views.login_student, name='login'),
    #  ex: /logout
    path(r'logout/', views.logout_student, name='logout'),
    path('api/', include('apis.urls')),
]
