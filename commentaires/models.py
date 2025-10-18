from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from articles.models import Article

User = get_user_model()


class Commentaire(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    article = models.ForeignKey(
        Article, on_delete=models.SET_NULL, null=True, blank=True
    )
    content = models.CharField(max_length=255, null=False)
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.content
