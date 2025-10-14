from rest_framework import serializers
from .models import File

class FileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = File
        fields = ('id', 'name', 'file', 'file_url', 'size', 'user', 'uploaded_at')
        read_only_fields = ('id', 'size', 'user', 'uploaded_at')
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None