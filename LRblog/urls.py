"""Myblogsys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path,re_path
from blog import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('index/', views.index),
    path('logout/', views.logout),
    path('', views.index),
    path('Up_down/',views.Up_down),
    path('comment/', views.comment),

    path('backend/',views.back),

    path('backend/add_article/', views.add_article),
    path('modify/',views.modify),
    path('omit',views.omit),

    path('upload/', views.upload),
    re_path('(?P<username>\w+)/$', views.homesite), #写URL时一定要看好，
    # 不能影响下面的URL分发，一旦前边的匹配了，没有后面的规则就会屏蔽前面相同的其余url
    re_path(r'(?P<username>\w+)/(?P<select>category|tag|date)/(?P<cont>.*)', views.homesite),
    re_path(r'(?P<username>\w+)/article/(?P<article_id>\d+)',views.article_detail),

]
