from django.db import models
from django.conf import settings


class Session(models.Model):
    TYPE_CHOICES = [
        ('one_on_one', 'One-on-One'),
        ('group', 'Group Session'),
        ('workshop', 'Workshop'),
        ('sports', 'Sports'),
        ('cultural', 'Cultural'),
        ('academic', 'Academic'),
        ('extracurricular', 'Extracurricular'),
    ]
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentor_sessions')
    title = models.CharField(max_length=300)
    description = models.TextField()
    session_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='upcoming')
    scheduled_at = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    max_participants = models.IntegerField(default=1)
    location = models.CharField(max_length=300, blank=True, help_text='Physical or virtual location')
    meeting_link = models.URLField(blank=True)
    image = models.ImageField(upload_to='sessions/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_at']

    def __str__(self):
        return f"{self.title} by {self.mentor}"

    @property
    def available_slots(self):
        return self.max_participants - self.bookings.filter(status='confirmed').count()

    @property
    def is_available(self):
        return self.available_slots > 0


class SessionBooking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('waitlisted', 'Waitlisted'),
    ]
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='bookings')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='session_bookings')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='confirmed')
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['session', 'student']

    def __str__(self):
        return f"{self.student} booked {self.session.title}"
