from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, help_text="Django session ID to group messages by conversation")

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'

    def __str__(self):
        return f"{self.user.username} - {self.role} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    @classmethod
    def get_chat_history(cls, user, session_id):
        """Get chat history for a specific user and session"""
        return cls.objects.filter(user=user, session_id=session_id).order_by('timestamp')

    @classmethod
    def clear_chat_history(cls, user, session_id):
        """Clear chat history for a specific user and session"""
        cls.objects.filter(user=user, session_id=session_id).delete() 