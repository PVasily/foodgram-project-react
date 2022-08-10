from rest_framework import viewsets
from rest_framework.decorators import action

from .serializers import (RecipeCreateSerializer,
                         RecipeReadSerializer,
                         IngredientSerializer,
                         UserSerializer)
from .models import Recipe, Ingredient, User


class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('pk')

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', 'DELETE'):
            return RecipeCreateSerializer
        return RecipeReadSerializer

    @action(detail=True)
    def recipes(self, request):
        print(request.user)
        if request.user.is_athenticated and (self.get_serializer_class == RecipeCreateSerializer):
            recipe = Recipe.objects.all().order_by('pk')
            serializer = self.get_serializer(author=request.user)
        return serializer.data

class IngredientViewset(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().order_by('pk')
    serializer_class = IngredientSerializer
