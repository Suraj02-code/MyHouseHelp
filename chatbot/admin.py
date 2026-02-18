from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ChatSession, ChatMessage, ChatbotKnowledge, 
    ChatbotIntent, ChatbotEntity, ChatbotAnalytics
)


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'created_at', 'updated_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'user']
    search_fields = ['session_id', 'user__username', 'user__email']
    readonly_fields = ['session_id', 'created_at', 'updated_at']
    ordering = ['-updated_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'message_type', 'content_preview', 'timestamp', 'is_read']
    list_filter = ['message_type', 'timestamp', 'is_read']
    search_fields = ['content', 'session__session_id', 'session__user__username']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(ChatbotKnowledge)
class ChatbotKnowledgeAdmin(admin.ModelAdmin):
    list_display = ['question_preview', 'category', 'intent', 'usage_count', 'confidence_score', 'is_active']
    list_filter = ['category', 'intent', 'is_active', 'created_at']
    search_fields = ['question', 'answer', 'keywords']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'question', 'answer', 'keywords')
        }),
        ('AI Enhancement', {
            'fields': ('intent', 'entities', 'confidence_score'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('usage_count', 'is_active'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def question_preview(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_preview.short_description = 'Question'


@admin.register(ChatbotIntent)
class ChatbotIntentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description_preview', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    def description_preview(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description'


@admin.register(ChatbotEntity)
class ChatbotEntityAdmin(admin.ModelAdmin):
    list_display = ['name', 'entity_type', 'value', 'synonyms_preview', 'is_active']
    list_filter = ['entity_type', 'is_active', 'created_at']
    search_fields = ['name', 'value']
    readonly_fields = ['created_at']
    
    def synonyms_preview(self, obj):
        if obj.synonyms:
            return ', '.join(obj.synonyms[:3]) + ('...' if len(obj.synonyms) > 3 else '')
        return '-'
    synonyms_preview.short_description = 'Synonyms'


@admin.register(ChatbotAnalytics)
class ChatbotAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['session', 'intent_detected', 'response_time', 'user_satisfaction', 'resolved', 'created_at']
    list_filter = ['intent_detected', 'resolved', 'user_satisfaction', 'created_at']
    search_fields = ['session__session_id', 'intent_detected']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session')


# Custom admin dashboard
admin.site.site_header = "MyHouseHelp Chatbot Administration"
admin.site.site_title = "Chatbot Admin"
admin.site.index_title = "Chatbot Management"