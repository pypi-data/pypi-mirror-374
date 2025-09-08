from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import generate_serializer

class BaseCRUDViewSet(viewsets.ModelViewSet):
    """
    Generic CRUD ViewSet.
    Subclasses or dynamic creation will define model & serializer.
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, model=None, serializer=None, *args, **kwargs):
        if model:
            self.queryset = model.objects.all()
            self.serializer_class = serializer or generate_serializer(model)
        super().__init__(*args, **kwargs)
