from django.contrib import admin
from .models import Roadmap, RoadmapNode, UserNodeProgress


class RoadmapNodeInline(admin.TabularInline):
    model = RoadmapNode
    extra = 1


@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'category']
    inlines = [RoadmapNodeInline]


@admin.register(RoadmapNode)
class RoadmapNodeAdmin(admin.ModelAdmin):
    list_display = ['title', 'roadmap', 'parent', 'order']
    list_filter = ['roadmap']


@admin.register(UserNodeProgress)
class UserNodeProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'node', 'status', 'updated_at']
    list_filter = ['status']
