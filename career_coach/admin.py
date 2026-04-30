from django.contrib import admin
from .models import UserAPIKey, CoachConversation, CoachMessage, FAQEntry, CoachAnalytics


@admin.register(FAQEntry)
class FAQEntryAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'order', 'is_active')
    list_filter = ('category', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('question', 'answer')


@admin.register(CoachConversation)
class CoachConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'provider', 'created_at', 'is_archived')
    list_filter = ('provider', 'is_archived', 'created_at')
    search_fields = ('title', 'user__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CoachMessage)
class CoachMessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'role', 'short_content', 'created_at')
    list_filter = ('role',)
    
    def short_content(self, obj):
        return obj.content[:80] + '...' if len(obj.content) > 80 else obj.content
    short_content.short_description = 'Content'


@admin.register(CoachAnalytics)
class CoachAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'provider_used', 'total_queries', 'avg_response_time_ms')
    list_filter = ('provider_used', 'date')


@admin.register(UserAPIKey)
class UserAPIKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'created_at', 'last_used')
    list_filter = ('provider',)
    # Never show the encrypted key in admin
    exclude = ('encrypted_key',)
    readonly_fields = ('user', 'provider', 'created_at', 'last_used')
