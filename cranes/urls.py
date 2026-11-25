"""
Frontend URL patterns for cranes application.
"""
from django.urls import path
from . import views

app_name = 'cranes'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('designs/new/', views.create_design, name='create_design'),
    path('designs/<int:pk>/', views.drawing_preview, name='drawing_preview'),
    path('designs/<int:pk>/edit/', views.design_detail, name='design_detail'),
    path('designs/<int:pk>/delete/', views.delete_design, name='delete_design'),
    path('designs/<int:pk>/download-svg/', views.download_svg, name='download_svg'),
]
