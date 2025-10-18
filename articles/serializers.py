from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Article, ArticleAttachment


class ArticleAttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ArticleAttachment
        fields = ["id", "file", "file_url", "name", "size", "file_type", "uploaded_at"]
        read_only_fields = ["id", "size", "file_type", "uploaded_at"]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class AuthorSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role"]

    def get_role(self, obj):
        try:
            return obj.role.role
        except:
            return "user"


class ArticleSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    attachments = ArticleAttachmentSerializer(many=True, read_only=True)
    attachments_count = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "status",
            "author",
            "attachments",
            "attachments_count",
            "is_deleted",
            "deleted_at",
            "created_at",
            "updated_at",
            "published_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "author",
            "is_deleted",
            "deleted_at",
            "published_at",
        ]

    def get_attachments_count(self, obj):
        return obj.attachments.count()


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    attachment_files = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False, allow_empty=True
    )
    attachments = ArticleAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "status",
            "attachment_files",
            "attachments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_status(self, value):
        request = self.context.get("request")
        user = request.user if request else None

        # Check if user can set status to published
        if value == "published":
            try:
                user_role = user.role.role
                if user_role not in ["admin", "moderator"]:
                    raise serializers.ValidationError(
                        "Seuls les administrateurs et modérateurs peuvent publier un article"
                    )
            except:
                raise serializers.ValidationError(
                    "Vous n'avez pas les permissions pour publier un article"
                )

        return value

    def create(self, validated_data):
        attachment_files = validated_data.pop("attachment_files", [])

        # Set default status to pending for authors
        user = self.context["request"].user
        try:
            user_role = user.role.role
            if user_role == "author" and validated_data.get("status") == "draft":
                validated_data["status"] = "pending"
        except:
            pass

        article = Article.objects.create(**validated_data)

        # Create attachments
        for file in attachment_files:
            ArticleAttachment.objects.create(article=article, file=file, name=file.name)

        return article

    def update(self, instance, validated_data):
        attachment_files = validated_data.pop("attachment_files", [])

        # Update article fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Add new attachments (don't delete existing ones)
        for file in attachment_files:
            ArticleAttachment.objects.create(
                article=instance, file=file, name=file.name
            )

        return instance


class ArticleListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    attachments_count = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "slug",
            "excerpt",
            "status",
            "author",
            "attachments_count",
            "created_at",
            "updated_at",
            "published_at",
        ]

    def get_attachments_count(self, obj):
        return obj.attachments.count()

    def get_excerpt(self, obj):
        if len(obj.content) > 200:
            return obj.content[:200] + "..."
        return obj.content
