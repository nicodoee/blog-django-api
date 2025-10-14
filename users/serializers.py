from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserRole

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']

    def get_role(self, obj):
        try:
            return obj.role.role
        except UserRole.DoesNotExist:
            return 'user'

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({'password': 'Les mots de passe ne correspondent pas'})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        UserRole.objects.create(user=user, role='user')
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)