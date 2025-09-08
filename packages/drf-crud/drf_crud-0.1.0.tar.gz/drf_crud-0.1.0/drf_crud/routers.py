from rest_framework.routers import DefaultRouter
from .viewsets import BaseCRUDViewSet
from .serializers import generate_serializer

def register_crud(router: DefaultRouter, prefix, model, serializer=None, basename=None):
    """
    Registers CRUD routes for the given model automatically.
    """
    viewset = type(
        f"{model.__name__}ViewSet",
        (BaseCRUDViewSet,),
        {},
    )(model=model, serializer=serializer)

    router.register(prefix, viewset, basename=basename or model.__name__.lower())
    return router
