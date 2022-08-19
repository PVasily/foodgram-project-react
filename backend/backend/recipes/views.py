from django.shortcuts import get_list_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response


from .serializers import (FollowSerializer,
                         RecipeReadSerializer, RecipeWriteSerializer, TagSerializer,
                         IngredientSerializer,
                         TagSerializer, CustomUserSerializer)
from .models import Follow, Recipe, Ingredient, Tag
from users.models import CustomUser


class UserViewset(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('pk')

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', 'DELETE'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = RecipeReadSerializer(instance=serializer.instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


class IngredientViewset(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().order_by('pk')
    serializer_class = IngredientSerializer

    # def get_serializer_class(self):
    #     if self.request.method in ('POST', 'PATCH', 'DELETE'):
    #         return IngredientSerializer
    #     return IngredientReadSerializer


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
