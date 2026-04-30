from django.db import models
from django.conf import settings


class UserAPIKey(models.Model):
    """Stores encrypted API keys for logged-in users."""
    PROVIDER_CHOICES = [
        ('openrouter', 'OpenRouter'),
        ('nvidia', 'NVIDIA NIM'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_api_keys'
    )
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    encrypted_key = models.TextField(help_text='Fernet-encrypted API key')
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'provider']
        verbose_name = 'User API Key'
        verbose_name_plural = 'User API Keys'

    def __str__(self):
        return f"{self.user.username} — {self.get_provider_display()}"


class CoachConversation(models.Model):
    """Chat session for logged-in users."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coach_conversations'
    )
    title = models.CharField(max_length=200, blank=True)
    provider = models.CharField(max_length=20, default='openrouter')
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title or f"Conversation #{self.pk}"


class CoachMessage(models.Model):
    """Individual message in a conversation."""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    conversation = models.ForeignKey(
        CoachConversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    token_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:60]}"


class FAQEntry(models.Model):
    """Pre-built career FAQ entries."""
    CATEGORY_CHOICES = [
        ('resume', 'Resume & CV'),
        ('interview', 'Interview Prep'),
        ('skills', 'Skill Development'),
        ('industry', 'Industry Insights'),
        ('networking', 'Networking'),
        ('general', 'General Career'),
    ]
    question = models.CharField(max_length=500)
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'FAQ Entry'
        verbose_name_plural = 'FAQ Entries'

    def __str__(self):
        return self.question[:80]


class CoachAnalytics(models.Model):
    """Anonymized usage statistics."""
    date = models.DateField()
    total_queries = models.IntegerField(default=0)
    topic_category = models.CharField(max_length=50, blank=True)
    provider_used = models.CharField(max_length=20, blank=True)
    avg_response_time_ms = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Coach Analytics'
        verbose_name_plural = 'Coach Analytics'

    def __str__(self):
        return f"{self.date} — {self.total_queries} queries"
