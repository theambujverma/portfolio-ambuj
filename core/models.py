from django.contrib.auth import get_user_model
from django.db import models


class Project(models.Model):
    STATUS_CHOICES = [
        ('live', '🟢 LIVE'),
        ('wip', '🟡 WIP'),
        ('private', '🔒 Private'),
    ]

    title = models.CharField(max_length=200)
    domain = models.CharField(max_length=200)
    url = models.URLField(blank=True, null=True)
    description = models.TextField()
    tags = models.CharField(max_length=200, help_text="Comma-separated tags (e.g. Django, PostgreSQL)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='live')
    is_home = models.BooleanField(default=True, verbose_name="Show on Home page")
    is_blog = models.BooleanField(default=True, verbose_name="Show on Blog page")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='profile')
    photo = models.FileField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return self.user.username
