"""
REST API URL routing for cranes app.
"""
from django.urls import path
from .api_views import (
    CraneDesignListCreateAPIView,
    CraneDesignDetailAPIView,
    CraneDesignGenerateDrawingAPIView,
    CranePreviewAPIView,
)

app_name = 'cranes_api'

urlpatterns = [
    path('designs/', CraneDesignListCreateAPIView.as_view(), name='design_list_create'),
    path('designs/<int:pk>/', CraneDesignDetailAPIView.as_view(), name='design_detail'),
    path('designs/<int:pk>/generate-drawing/', CraneDesignGenerateDrawingAPIView.as_view(), name='generate_drawing'),
    path('designs/preview/', CranePreviewAPIView.as_view(), name='preview_drawing'),
]
