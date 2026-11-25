"""
URL configuration for crane_generator project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('cranes.api_urls')),
    path('', include('cranes.urls')),
]
