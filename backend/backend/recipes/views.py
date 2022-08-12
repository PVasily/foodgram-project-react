from django.shortcuts import get_list_or_404
from rest_framework import viewsets

from .serializers import (FollowSerializer, RecipeCreateSerializer,
                         RecipeReadSerializer, TagSerializer,
                         IngredientSerializer, IngredientReadSerializer,
                         TagSerializer)
from .models import Follow, Recipe, Ingredient, Tag, User


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('pk')

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', 'DELETE'):
            return RecipeCreateSerializer
        return RecipeReadSerializer

    # def perform_create(self, serializer):
    #     author = self.request.user
    #     serializer.save(author=author)


class IngredientViewset(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().order_by('pk')
    serializer_class = IngredientSerializer

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', 'DELETE'):
            return IngredientSerializer
        return IngredientReadSerializer


class TagViewset(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer


class FollowVieset(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer


# class CartViewset(viewsets.ModelViewSet):
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer

#     def create(self, request, *args, **kwargs):
#         recipes = get_list_or_404(Recipe, author=request.user)
#         for recipe in recipes:
#             print(recipe.ingredients[0])
#         return super().create(request, *args, **kwargs)

#     def get_queryset(self):
#         return super().get_queryset()
