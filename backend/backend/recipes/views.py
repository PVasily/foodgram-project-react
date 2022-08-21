from crypt import methods
from django.shortcuts import get_list_or_404, get_object_or_404
from users.serializers import UserSerializer
from users.views import UserViewset

from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination

from users.models import User

from .serializers import (CartReadSerializer, CartWriteSerializer, FavoriteRecipeSerializer, RecipeCreateSerializer, RecipeForCartAndFavoriteSerializer,
                         RecipeReadSerializer, SubscriptionSerializer, TagSerializer,
                         IngredientSerializer,
                         TagSerializer)
from .models import Cart, Favorite, Follow, Recipe, Ingredient, Tag


class CreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass


class MainPageViewset(viewsets.ModelViewSet):
    serializer_class = RecipeReadSerializer
    queryset = Recipe.objects.all().order_by('-pub_date')
    pagination_class = PageNumberPagination


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('pk')

    def get_serializer_class(self):
        print('STEP 2')
        if self.request.method in ('POST', 'PATCH', 'DELETE'):
            return RecipeCreateSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = RecipeReadSerializer(instance=serializer.instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # @staticmethod
    # def add_to_cart(request, pk, serializers):
    #     user = request.user
    #     recipe = Recipe.objects.get(id=pk)
    #     Cart.objects.create(user=user, recipe=recipe)
    #     return Response(serializers.data)

    # @action(detail=True, methods=["POST"],
    #         permission_classes=[IsAuthenticated])
    # def shopping_cart(self, request, pk):
    #     user = request.user
    #     recipe = Recipe.objects.get(id=pk)
    #     # Cart.objects.create(user=user, recipe=recipe)
    #     serializer = CartWriteSerializer(instance=serializer.instance) 
    #     return Response(serializer.data)
    #     # print(request.user)
    #     # return self.add_to_cart(
    #     #     request=request, pk=pk, serializers=CartRecipeWriteSerializer)


class IngredientViewset(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().order_by('pk')
    serializer_class = IngredientSerializer


class TagViewset(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer


class CartViewset(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = FavoriteRecipeSerializer

    @action(detail=True, methods=['POST', 'DELETE'], url_path='shopping_cart')
    def favorite(self, request, pk):
        current_user = self.request.user
        if current_user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe_in_favorite = Cart.objects.filter(user=current_user, recipe=recipe)
        if request.method == 'POST':
            if recipe_in_favorite.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Cart.objects.create(user=current_user, recipe=recipe)
            serializer = FavoriteRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not recipe_in_favorite.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            recipe_in_favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    # @action(
    #     detail=False,
    #     methods=['get']
    # )
    # def shopping_cart(self, request):
    #     user = request.user
    #     print(user)
    #     recipes = Cart.objects.filter(user=user)
    #     return recipes

    # @action(
    #     detail=True,
    #     methods=['post']
    # )
    # def shopping_cart(self, request, pk=None):
    #     print(request.data)
    
    # def get_serializer_class(self):
    #     if self.request.method == 'GET':
    #         return CartReadSerializer
    #     return CartWriteSerializer

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)

    # def create(self, request, *args, **kwargs):
    #     if request.method == 'GET':
    #         recipes = get_object_or_404(Recipe, author=request.user)
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     serializer = CartRecipeWriteSerializer(instance=serializer.instance)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)


# class FollowViewset(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = FollowSerializer

#     @action(
#         detail=False,
#         methods=['POST', 'DELETE']
#     )
#     def subscribe(self, request, *args, **kwargs):
#         follower = request.user
#         print(request.data)
#         following_id = self.kwargs.get('id')
#         following = get_object_or_404(User, id=following_id)
        
#         if request.metod == 'POST':
#             serializer_class = self.get_serializer_class()
#             serializer = serializer_class(
#                 following,
#                 data=request.data,
#                 context={'request': request}
#             )
#             serializer.is_valid(raise_exception=True)
#             Follow.objects.create(follower=follower, following=following)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         if request.method == 'DELETE':
#             subscr = get_object_or_404(Follow, follower=follower, following=following)
#             subscr.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteRecipeSerializer

    @action(detail=True, methods=['POST', 'DELETE'], url_path='favorited')
    def favorite(self, request, pk):
        current_user = self.request.user
        if current_user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe_in_favorite = Favorite.objects.filter(user=current_user, recipe=recipe)
        if request.method == 'POST':
            if recipe_in_favorite.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=current_user, recipe=recipe)
            serializer = FavoriteRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not recipe_in_favorite.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            recipe_in_favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    # def get_queryset(self):
    #     print(self.kwargs.get('id'))
    #     recipes_id = self.kwargs.get('id')
    #     recipes = get_object_or_404(Recipe, pk=recipes_id)
    #     queryset = recipes.favorites.all()
    #     return queryset

    # def perform_create(self, serializer):

    #     recipe_id = self.kwargs.get('id')
    #     recipe = get_object_or_404(Recipe, id=recipe_id)
    #     exist=Favorite.objects.filter(
    #         recipe=recipe,
    #         user=self.request.user,
    #         is_favorite=True
    #     ).exists()
    #     if self.request.user != recipe.author and exist != True:
    #         return Response(serializer.save(user=self.request.user, recipe=recipe, is_favorite=True), status=status.HTTP_200_OK)
    #     return Response(status=status.HTTP_400_BAD_REQUEST)

    # @action(detail=True, methods=['delete'])
    # def favorite(self, request, pk=None):
    #     Favorite.objects.get(recipe__id=pk).delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


class CustomUserViewSet(UserViewset):
    queryset = User.objects.all()
    serializer_class = SubscriptionSerializer
    # pagination_class = PageLimitPaginator

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        print('HELLO')
        user_subscriptions = User.objects.filter(author__user=request.user)
        print(user_subscriptions)
        serializer = SubscriptionSerializer(
            user_subscriptions,
            context=self.get_serializer_context(),
            many=True
        )
        return Response(serializer.data)     
