from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response

from core.utils import get_shopping_list
from core.filters import IngredientFilter, RecipeFilter
from core.mixins import IngredientsTagsMixin, ListCartFavoriteMixin
from .models import Cart, Favorite, Ingredient, Recipe, Tag
from .serializers import (
    AnonymousRecipeReadSerializer, IngredientSerializer, LightRecipeSerializer,
    RecipeCreateSerializer, RecipeReadSerializer,
    TagSerializer
)


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AllowAny, )
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', 'DELETE'):
            return RecipeCreateSerializer
        if self.request.user.is_anonymous:
            return AnonymousRecipeReadSerializer
        return RecipeReadSerializer

    @staticmethod
    def _set_action_for_recipe(model, user, method, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        target_recipe = model.objects.filter(
            user=user,
            recipe=recipe
        )
        if method == 'POST':
            model.objects.create(user=user, recipe=recipe)
            serializer = LightRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        target_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated | IsAdminUser, )
    )
    def shopping_cart(self, request, pk):
        print(request.user, request.method)
        return self._set_action_for_recipe(
            Cart,
            request.user,
            request.method,
            pk
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='favorite',
        permission_classes=(IsAuthenticated | IsAdminUser, )
    )
    def favorite(self, request, pk):
        return self._set_action_for_recipe(
            Favorite,
            request.user,
            request.method,
            pk
        )

    @action(detail=False, methods=['GET'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        user = request.user
        main_list = get_shopping_list(user)
        response = HttpResponse(main_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="Cart.txt"'
        return response


class IngredientViewset(IngredientsTagsMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = IngredientFilter


class TagViewset(IngredientsTagsMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class ListCartViewSet(ListCartFavoriteMixin):

    def get_queryset(self):
        user = self.request.user
        return Recipe.objects.filter(cart_recipes__user=user)


class ListFavoriteViewSet(ListCartFavoriteMixin):

    def get_queryset(self, ):
        user = self.request.user
        return Recipe.objects.filter(favorite_recipes__user=user)
