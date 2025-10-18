from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserRole


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="role.role", read_only=True, default="user")

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    user_role = serializers.ChoiceField(
        choices=UserRole.ROLE_CHOICES, default="author", write_only=True, required=False
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "user_role",
        ]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur existe déjà")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé")
        return value

    def validate(self, data):
        if data["password"] != data.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password": "Les mots de passe ne correspondent pas"}
            )
        return data

    def create(self, validated_data):
        user_role = validated_data.pop("user_role", "user")
        user = User.objects.create_user(**validated_data)
        UserRole.objects.create(user=user, role=user_role)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password": "Les mots de passe ne correspondent pas"}
            )
        return data


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def validate_email(self, value):
        user = self.context["request"].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("Cet email est deja utilise")
        return value
