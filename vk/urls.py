from django.urls import path
from . import views

urlpatterns = [
    path('vkreceiver/', views.vkreceiver, name='vkreceiver'),



]

