from django.conf import settings
from django.db import models


class CustomerQuery(models.Model):
    class Category(models.TextChoices):
        TECHNICAL = "Technical", "Technical"
        BILLING = "Billing", "Billing"
        GENERAL = "General", "General"
        ACCOUNT = "Account Related", "Account Related"

    class Priority(models.TextChoices):
        LOW = "Low", "Low"
        MEDIUM = "Medium", "Medium"
        HIGH = "High", "High"

    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        IN_PROGRESS = "In Progress", "In Progress"
        RESOLVED = "Resolved", "Resolved"

    customer_name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices, blank=True, null=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, blank=True, null=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    suggested_response = models.TextField(blank=True, default="")
    ai_source = models.CharField(max_length=20, blank=True, default="")  # "gemini" | "fallback"
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name="queries")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "customer queries"

    def __str__(self):
        return f"#{self.pk} {self.subject} ({self.status})"
