from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return super().get_queryset()
