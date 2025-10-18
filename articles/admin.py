from django.contrib import admin
from .models import Article, ArticleAttachment

class ArticleAttachmentInline(admin.TabularInline):
    model = ArticleAttachment
    extra = 1
    readonly_fields = ['size', 'file_type', 'uploaded_at']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'is_deleted', 'created_at', 'published_at']
    list_filter = ['status', 'is_deleted', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'published_at', 'deleted_at']
    inlines = [ArticleAttachmentInline]

    fieldsets = (
        ('Informations de base', {
            'fields': ('title', 'slug', 'author', 'content')
        }),
        ('Statut', {
            'fields': ('status', 'published_at')
        }),
        ('Suppression', {
            'fields': ('is_deleted', 'deleted_at')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ArticleAttachment)
class ArticleAttachmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'article', 'file_type', 'size', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['name', 'article__title']
    readonly_fields = ['size', 'file_type', 'uploaded_at']