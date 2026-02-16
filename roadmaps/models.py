from django.db import models
from django.conf import settings


class Roadmap(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    CATEGORY_CHOICES = [
        ('web', 'Web Development'),
        ('data', 'Data Science'),
        ('mobile', 'Mobile Development'),
        ('devops', 'DevOps'),
        ('ai', 'AI / Machine Learning'),
        ('design', 'UI/UX Design'),
        ('backend', 'Backend'),
        ('frontend', 'Frontend'),
        ('security', 'Cyber Security'),
        ('other', 'Other'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='roadmaps')
    rejection_feedback = models.TextField(blank=True, help_text='Admin feedback if rejected')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def node_count(self):
        return self.nodes.count()


class RoadmapNode(models.Model):
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='nodes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    resources_text = models.TextField(blank=True, help_text='Links or references for this topic')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.roadmap.title} → {self.title}"


class UserNodeProgress(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('skipped', 'Skipped'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='roadmap_progress')
    node = models.ForeignKey(RoadmapNode, on_delete=models.CASCADE, related_name='user_progress')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='not_started')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'node']

    def __str__(self):
        return f"{self.user.username} - {self.node.title}: {self.status}"
