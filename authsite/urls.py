from django.urls import path, include
from authsite import views
from django.contrib.auth import views as auth_views


urlpatterns = [

    path('vk_auth/', views.vk_auth, name='vk_auth'),
    path('vk_auth_callback/', views.vk_auth_callback, name='vk_auth_callback'),
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("access_denied/", views.access_denied, name="access_denied"),



]
