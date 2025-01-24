from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'content_preview', 'timestamp', 'session_id')
    list_filter = ('role', 'timestamp', 'user')
    search_fields = ('content', 'user__username', 'session_id')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    
    def content_preview(self, obj):
        """Return a preview of the message content"""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview' 