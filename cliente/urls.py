from django.urls import path
from . import views

app_name = 'cliente'

urlpatterns = [
    path('', views.home, name='home'),
]