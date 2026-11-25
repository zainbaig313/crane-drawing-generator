"""
Django admin configuration for CraneDesign.
"""
from django.contrib import admin
from .models import CraneDesign


@admin.register(CraneDesign)
class CraneDesignAdmin(admin.ModelAdmin):
    list_display = ('design_name', 'capacity', 'span', 'lifting_height', 'created_at', 'updated_at')
    list_filter = ('crane_type', 'created_at')
    search_fields = ('design_name',)
    readonly_fields = ('created_at', 'updated_at')
