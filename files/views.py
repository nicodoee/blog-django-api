from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import File
from .serializers import FileSerializer

class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return File.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['delete'])
    def delete_file(self, request, pk=None):
        file_obj = self.get_object()
        file_obj.file.delete()
        file_obj.delete()
        return Response({'detail': 'Fichier supprimé'}, status=status.HTTP_204_NO_CONTENT)