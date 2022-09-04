from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from core.utils import get_shopping_list
from core.filters import IngredientFilter, RecipeFilter
from core.permissions import IsAuthAndAuthorOrReadOnly
from .models import Cart, Favorite, Ingredient, Recipe, Tag
from .serializers import (
    IngredientSerializer, LightRecipeSerializer,
    RecipeCreateSerializer, RecipeReadSerializer,
    TagSerializer
)


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthAndAuthorOrReadOnly, )
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', 'DELETE'):
            return RecipeCreateSerializer
        return RecipeReadSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe_in_favorite = Cart.objects.filter(
            user=user,
            recipe=recipe
        )
        if request.method == 'POST':
            Cart.objects.create(user=user, recipe=recipe)
            serializer = LightRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        recipe_in_favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'], url_path='favorite')
    def favorite(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe_in_favorite = Favorite.objects.filter(
            user=user,
            recipe=recipe
        )
        if request.method == 'POST':
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = LightRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        recipe_in_favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        user = request.user
        main_list = get_shopping_list(user)
        response = HttpResponse(main_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="Cart.txt"'
        return response


class IngredientViewset(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminUser,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = IngredientFilter


class TagViewset(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAdminUser,)


class ListCartViewSet(viewsets.ModelViewSet):
    serializer_class = LightRecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Recipe.objects.filter(cart_recipes__user=user)


class ListFavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = LightRecipeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, ):
        user = self.request.user
        return Recipe.objects.filter(favorite_recipes__user=user)
