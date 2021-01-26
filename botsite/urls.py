from django.urls import path

from botsite import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('test/', views.test, name='test'),
    # path('conversations/<int:conversation>/random_post/', views.random_post, name='random_post'),
    # path('conversations/<int:pk>/random_post/', views.ChatSettingUpdate.as_view(), name='random_post'),
    path('account_creation_info/', views.account_creation_info, name='account_creation_info'),
    path('conversations/<int:conversation>/', views.conversation_settings, name='bot_settings'),




]
