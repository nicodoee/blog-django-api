from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import Article, ArticleAttachment
from .serializers import (
    ArticleSerializer, 
    ArticleCreateUpdateSerializer, 
    ArticleListSerializer,
    ArticleAttachmentSerializer
)
from .permissions import (
    CanCreateArticle,
    IsAuthorOrModeratorOrAdmin,
    CanPublishArticle,
    CanDeleteArticle,
    CanViewArticle
)

class ArticlePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ArticleViewSet(viewsets.ModelViewSet):
    pagination_class = ArticlePagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ArticleCreateUpdateSerializer
        return ArticleSerializer
    
    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        elif self.action == 'retrieve':
            return [IsAuthenticated(), CanViewArticle()]
        elif self.action == 'create':
            return [IsAuthenticated(), CanCreateArticle()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsAuthorOrModeratorOrAdmin()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), CanDeleteArticle()]
        elif self.action == 'publish':
            return [IsAuthenticated(), CanPublishArticle()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = Article.objects.select_related('author', 'author__role').prefetch_related('attachments')
        
        # Filter by status based on user role
        user = self.request.user
        
        if not user.is_authenticated:
            # Anonymous users: only published, non-deleted articles
            return queryset.filter(status='published', is_deleted=False)
        
        try:
            user_role = user.role.role
            
            if user_role in ['admin', 'moderator']:
                # Admin/Moderator: see everything
                pass
            elif user_role == 'author':
                # Authors: see their own + published articles
                queryset = queryset.filter(
                    Q(author=user) | Q(status='published', is_deleted=False)
                )
            else:
                # Regular users: only published, non-deleted
                queryset = queryset.filter(status='published', is_deleted=False)
        except:
            # Users without role: only published, non-deleted
            queryset = queryset.filter(status='published', is_deleted=False)
        
        # Filter by status query param
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by deleted
        show_deleted = self.request.query_params.get('deleted', None)
        if show_deleted == 'true':
            try:
                user_role = user.role.role
                if user_role in ['admin', 'moderator']:
                    queryset = queryset.filter(is_deleted=True)
            except:
                pass
        elif show_deleted != 'all':
            queryset = queryset.filter(is_deleted=False)
        
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        
        # Set default status based on role
        try:
            user_role = user.role.role
            if user_role == 'author':
                # Authors create articles in pending status by default
                serializer.save(author=user, status='pending')
            else:
                # Admin/Moderator can set any status
                serializer.save(author=user)
        except:
            serializer.save(author=user, status='pending')
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete"""
        article = self.get_object()
        article.soft_delete()
        return Response(
            {'detail': 'Article supprimé avec succès'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=True, methods=['post'], url_path='publish')
    def publish(self, request, pk=None):
        """Publish an article (admin/moderator only)"""
        article = self.get_object()
        
        if article.is_deleted:
            return Response(
                {'error': 'Impossible de publier un article supprimé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        article.status = 'published'
        article.save()
        
        serializer = self.get_serializer(article)
        return Response(
            {
                'detail': 'Article publié avec succès',
                'article': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        """Restore a soft-deleted article"""
        article = self.get_object()
        
        if not article.is_deleted:
            return Response(
                {'error': 'Cet article n\'est pas supprimé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        article.restore()
        
        serializer = self.get_serializer(article)
        return Response(
            {
                'detail': 'Article restauré avec succès',
                'article': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], url_path='add-attachment')
    def add_attachment(self, request, pk=None):
        """Add attachment to existing article"""
        article = self.get_object()
        
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'Aucun fichier fourni'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attachment = ArticleAttachment.objects.create(
            article=article,
            file=file,
            name=request.data.get('name', file.name)
        )
        
        serializer = ArticleAttachmentSerializer(attachment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], url_path='remove-attachment/(?P<attachment_id>[^/.]+)')
    def remove_attachment(self, request, pk=None, attachment_id=None):
        """Remove attachment from article"""
        article = self.get_object()
        
        try:
            attachment = article.attachments.get(id=attachment_id)
            attachment.file.delete()
            attachment.delete()
            return Response(
                {'detail': 'Pièce jointe supprimée'},
                status=status.HTTP_204_NO_CONTENT
            )
        except ArticleAttachment.DoesNotExist:
            return Response(
                {'error': 'Pièce jointe introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )