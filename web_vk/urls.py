from django.contrib import admin
from django.urls import path, include
import vk.views
import vk.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('vk.urls')),
    path('', include('botsite.urls')),
    path('', include('authsite.urls')),
    path('capacity/', vk.views.capacity_test),
    path('capacity2/', vk.views.capacity_test2),

]
handler500 = 'botsite.views.error_500'
handler404 = 'botsite.views.error_404'
