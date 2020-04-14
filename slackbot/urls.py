from django.urls import include, path
from . import views


urlpatterns = [
    path('event/hook/', views.event_hook, name='event_hook'),
    path('event/slash/', views.slash_command, name='slash_command'),
]