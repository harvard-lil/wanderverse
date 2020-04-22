"""wanderverse URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from app import views
urlpatterns = [
    path('', views.index, name="home"),
    path('admin/', admin.site.urls),
    path('poem/<int:poem_id>/', views.read_poem, name="read"),
    path('poem/', views.read_poem, name="read_random"),
    path('add_line/<int:poem_id>/', views.add_line, name="add_line"),
    path('contribute/<int:poem_id>/', views.contribute, name="contribute"),
    path('contribute/', views.contribute, name="contribute_random"),
    path('slack/',  include('slackbot.urls'), name="slack"),
]
