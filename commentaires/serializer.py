from django.contrib.auth.models import User
from rest_framework import serializers

from articles.serializers import ArticleSerializer, AuthorSerializer

from .models import Commentaire


class CommentaireSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    article = ArticleSerializer(read_only=True)

    class Meta:
        model = Commentaire
        fields = ["id", "content"]


class CommentaireListSerializer(serializers.ModelSerializer):
    pass
