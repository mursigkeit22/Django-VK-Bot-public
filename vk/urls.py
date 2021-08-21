from django.urls import path
from . import views

urlpatterns = [
    path('vkreceiver/', views.vkreceiver, name='vkreceiver'),
    path('capacity/', views.capacity_test),
    path('capacity2/', views.capacity_test2),
    path('celery_test/', views.celery_test),
    path('celery_test2/', views.celery_test2),



]

