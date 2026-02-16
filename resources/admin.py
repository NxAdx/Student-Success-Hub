from django.contrib import admin
from .models import Category, Resource, ResourceBookmark

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'resource_type', 'difficulty', 'uploaded_by', 'views_count']
    list_filter = ['resource_type', 'difficulty', 'category']
    search_fields = ['title', 'description']

@admin.register(ResourceBookmark)
class ResourceBookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource']
