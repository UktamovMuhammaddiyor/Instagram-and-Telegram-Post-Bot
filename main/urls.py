from django.urls import path
from . import views


urlpatterns = [
    path('', views.index),
    path('login/', views.login),
    path('set_webhook/', views.set_webhook),
    path('getpost/', views.get_post),
]