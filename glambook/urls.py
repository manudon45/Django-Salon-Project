from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls), # Yahan urls hona chahiye
    path('', include('glambookapp.urls')),
    path('appointments/', include('appointments.urls')),
]