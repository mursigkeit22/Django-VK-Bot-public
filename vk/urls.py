from django.urls import path
from . import views  # Here we're importing all of our views from the blog application.

urlpatterns = [
    path('', views.home, name='home'), ]
