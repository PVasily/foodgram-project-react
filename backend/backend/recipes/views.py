from rest_framework import viewsets

from .serializers import (RecipeCreateSerializer,
                         RecipeReadSerializer,
                         IngredientSerializer)
from .models import Recipe, Ingredient


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('pk')

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', 'DELETE'):
            return RecipeCreateSerializer
        return RecipeReadSerializer


class IngredientViewset(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().order_by('pk')
    serializer_class = IngredientSerializer
