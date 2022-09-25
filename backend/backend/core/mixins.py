from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .permissions import IsAdminOrReadOnly
from recipes.serializers import LightRecipeSerializer


class IngredientsTagsMixin(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly, )
    pagination_class = None


class ListCartFavoriteMixin(viewsets.ModelViewSet):
    serializer_class = LightRecipeSerializer
    permission_classes = (IsAuthenticated | IsAdminUser, )
