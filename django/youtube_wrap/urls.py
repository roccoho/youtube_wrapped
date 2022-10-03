from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('display', views.display, name='display'),
    path('result', views.result, name='result'),
]