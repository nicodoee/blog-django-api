from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone


User = get_user_model()

class Article(models.Model):
  STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('pending', 'Pending'),
    ('published', 'Published'),
  ]

  author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
  title = models.CharField(max_length=255)
  slug = models.SlugField(max_length=255, unique=True, blank=True)
  content = models.TextField()
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

  # Soft delete
  is_deleted = models.BooleanField(default=False)
  deleted_at = models.DateTimeField(null=True, blank=True)

  # Timestamps
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  published_at = models.DateTimeField(null=True, blank=True)

  class Meta:
    ordering = ['-created_at']
    indexes = [
      models.Index(fields=['status', 'is_deleted']),
      models.Index(fields=['author', 'status']),
    ]

  def save(self, *args, **kwargs):
    if not self.slug:
      base_slug = slugify(self.title)
      slug = base_slug
      counter = 1
      while Article.objects.filter(slug=slug).exists():
          slug = f"{base_slug}-{counter}"
          counter += 1
      self.slug = slug

    # Set published_at when status changes to published
    if self.status == 'published' and not self.published_at:
      self.published_at = timezone.now()

    super().save(*args, **kwargs)

  def soft_delete(self):
    self.is_deleted = True
    self.deleted_at = timezone.now()
    self.save()

  def restore(self):
    self.is_deleted = False
    self.deleted_at = None
    self.save()

  def __str__(self):
    return self.title


class ArticleAttachment(models.Model):
  article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='attachments')
  file = models.FileField(upload_to='articles/attachments/%Y/%m/%d/')
  name = models.CharField(max_length=255)
  size = models.BigIntegerField(editable=False)
  file_type = models.CharField(max_length=100, blank=True)
  uploaded_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['uploaded_at']

  def save(self, *args, **kwargs):
    if self.file:
      self.size = self.file.size
      if not self.name:
        self.name = self.file.name
      # Get file extension/type
      if '.' in self.file.name:
        self.file_type = self.file.name.split('.')[-1].lower()
    super().save(*args, **kwargs)

  def __str__(self):
    return f"{self.article.title} - {self.name}"