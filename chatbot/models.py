from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class ChatSession(models.Model):
    """Chat session between user and chatbot"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='chat_sessions',
        null=True, 
        blank=True
    )
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        user_info = self.user.username if self.user else 'Anonymous'
        return f"Chat Session {self.session_id} - {user_info}"


class ChatMessage(models.Model):
    """Individual messages in a chat session"""
    
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('bot', 'Bot Response'),
        ('system', 'System Message'),
    ]
    
    session = models.ForeignKey(
        ChatSession, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.get_message_type_display()}: {self.content[:50]}..."


class ChatbotKnowledge(models.Model):
    """Knowledge base for chatbot responses"""
    
    CATEGORIES = [
        ('general', 'General Information'),
        ('services', 'Services'),
        ('booking', 'Booking Process'),
        ('pricing', 'Pricing'),
        ('support', 'Customer Support'),
        ('account', 'Account Management'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORIES)
    question = models.CharField(max_length=500)
    answer = models.TextField()
    keywords = models.TextField(
        help_text="Comma-separated keywords for matching questions"
    )
    intent = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Intent classification for this knowledge entry"
    )
    entities = models.JSONField(
        default=dict,
        blank=True,
        help_text="Extracted entities and their types"
    )
    confidence_score = models.FloatField(
        default=1.0,
        help_text="Confidence score for this knowledge entry"
    )
    usage_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'question']
    
    def __str__(self):
        return f"{self.category}: {self.question[:50]}..."
    
    def get_keywords_list(self):
        """Return keywords as a list"""
        return [keyword.strip().lower() for keyword in self.keywords.split(',') if keyword.strip()]
    
    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class ChatbotIntent(models.Model):
    """Intent classification for chatbot responses"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    examples = models.JSONField(
        default=list,
        help_text="Example phrases for this intent"
    )
    response_template = models.TextField(
        blank=True,
        help_text="Template for responses to this intent"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ChatbotEntity(models.Model):
    """Entity extraction for chatbot responses"""
    
    ENTITY_TYPES = [
        ('service', 'Service Type'),
        ('location', 'Location'),
        ('time', 'Time/Date'),
        ('price', 'Price'),
        ('person', 'Person Name'),
        ('contact', 'Contact Info'),
        ('custom', 'Custom Entity'),
    ]
    
    name = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    value = models.CharField(max_length=200)
    synonyms = models.JSONField(
        default=list,
        help_text="Synonyms for this entity"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['entity_type', 'name']
        unique_together = ['name', 'entity_type']
    
    def __str__(self):
        return f"{self.entity_type}: {self.name}"


class ChatbotAnalytics(models.Model):
    """Analytics data for chatbot performance"""
    
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    intent_detected = models.CharField(max_length=100, blank=True)
    entities_extracted = models.JSONField(default=dict)
    response_time = models.FloatField(help_text="Response time in seconds")
    user_satisfaction = models.IntegerField(
        null=True,
        blank=True,
        help_text="User satisfaction rating (1-5)"
    )
    conversation_length = models.PositiveIntegerField(
        help_text="Number of messages in conversation"
    )
    resolved = models.BooleanField(
        default=False,
        help_text="Whether the user's query was resolved"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Analytics for {self.session.session_id} - {self.intent_detected}"