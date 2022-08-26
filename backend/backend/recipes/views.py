from django.shortcuts import get_list_or_404, get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum

from rest_framework import viewsets, status, mixins, generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination

from users.models import User

from .serializers import (RecipeCreateSerializer, LightRecipeSerializer,
        RecipeReadSerializer, SubscriptionGetSerializer, TagSerializer,
        IngredientSerializer, TagSerializer
)
from .models import Cart, Favorite, Follow, Recipe, Ingredient, RecipeIngredient, Tag
from core.permissions import IsAuthOrReadOnly, IsAuthOrAdmin, IsAuthAndAuthorOrReadOnly
from core.filters import RecipeFilter, IngredientFilter, RecipeFilterMainPage
from users.serializers import UserSerializer


class CreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass


# class MainPageViewset(viewsets.ModelViewSet):
#     serializer_class = RecipeReadSerializer
#     queryset = Recipe.objects.all().order_by('-pub_date')
#     filter_backends = (DjangoFilterBackend,)
#     filter_class = RecipeFilterMainPage
#     permission_classes = (IsAuthOrReadOnly,)
#     pagination_class = PageNumberPagination


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('pk')
    permission_classes = [IsAuthAndAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', 'DELETE'):
            print('Hi')
            return RecipeCreateSerializer
        return RecipeReadSerializer


class IngredientViewset(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().order_by('pk')
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = IngredientFilter


class TagViewset(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticated,)


class CartViewset(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = LightRecipeSerializer
    # permission_classes = (IsAuthenticated)

    @action(
        detail=True,
        # permission_classes=(IsAuthOrAdmin),
        methods=['POST', 'DELETE'],
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk):
        current_user = self.request.user
        if current_user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe_in_favorite = Cart.objects.filter(user=current_user, recipe=recipe)
        if request.method == 'POST':
            if recipe_in_favorite.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Cart.objects.create(user=current_user, recipe=recipe)
            serializer = LightRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not recipe_in_favorite.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            recipe_in_favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class ListCartViewSet(viewsets.ModelViewSet):
    serializer_class = LightRecipeSerializer
    permission_classes = (IsAuthAndAuthorOrReadOnly,) #--?

    def get_queryset(self):
        user = self.request.user
        recipes_in_cart = Cart.objects.filter(user=user)
        queryset = [recipe.recipe for recipe in recipes_in_cart]
        # queryset = user.recipes.filter(cart_recipes__user=user)
        return queryset


class DownloadCartListViewset(ListCartViewSet):

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        shopping_list = {}
        ingredients = RecipeIngredient.objects.filter(
            recipe__cart_recipes__user=request.user
        ).values(
                'ingredient__name',
                'ingredient__measurement_unit'
        ).annotate(total=Sum('amount'))
        for ingredient in ingredients:
            amount = ingredient['total']
            name = ingredient['ingredient__name']
            measurement_unit = ingredient['ingredient__measurement_unit']
            shopping_list[name] = {
                'measurement_unit': measurement_unit,
                'amount': amount
            }
        main_list = ([f"{item}: {value['amount']}"
                      f" {value['measurement_unit']}\n"
                      for item, value in shopping_list.items()])
        response = HttpResponse(main_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="Cart.txt"'
        return response


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = LightRecipeSerializer
    permission_classes = (IsAuthAndAuthorOrReadOnly,) #---?

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
            serializer = LightRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not recipe_in_favorite.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            recipe_in_favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class ListFavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = LightRecipeSerializer
    permission_classes = (IsAuthAndAuthorOrReadOnly,) #---?

    def get_queryset(self, ):
        user = self.request.user
        recipes_in_cart = Favorite.objects.filter(user=user)
        queryset = [recipe.recipe for recipe in recipes_in_cart]
        # queryset = user.recipes.filter(favorite_recipes__user=user)
        print(queryset)
        return queryset


class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return UserSerializer
        return SubscriptionGetSerializer

    @action(
        detail=False,
        methods=['GET'],
        url_path='me'
    )
    def me(self, request):
        me = get_object_or_404(User, username=request.user)
        serializers = self.get_serializer(me)
        return Response(serializers.data, status=status.HTTP_200_OK)


class SubscUserViewSet(UserViewset):
    queryset = User.objects.all()
    serializer_class = SubscriptionGetSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthAndAuthorOrReadOnly,) #--?

    @action(
        detail=False,
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        user_subscriptions = User.objects.filter(following__user=request.user)
        serializer = SubscriptionGetSerializer(
            user_subscriptions,
            context=self.get_serializer_context(),
            many=True
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='subscribe'
    )
    def subscribe(self, request, pk=None):
        follower = request.user
        following = get_object_or_404(User, id=pk) 
        if request.method == 'POST':
            serializer_class = self.get_serializer_class()
            serializer = serializer_class(
                following,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=follower, author=following)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscr = get_object_or_404(Follow, user=follower, author=following)
            subscr.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ProfileViewset(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = SubscriptionGetSerializer


# class FollowViewset(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = SubscriptionGetSerializer

#     @action(
#         detail=True,
#         methods=['POST', 'DELETE'],
#         url_path='subscribe'
#     )
#     def subscribe(self, request, pk=None):
#         follower = request.user
#         print(request.data)
#         # following_id = self.kwargs.get('id')
#         following = get_object_or_404(User, id=pk)
        
#         if request.metod == 'POST':
#             serializer_class = self.get_serializer_class()
#             serializer = serializer_class(
#                 following,
#                 data=request.data,
#                 context={'request': request}
#             )
#             serializer.is_valid(raise_exception=True)
#             Follow.objects.create(user=follower, author=following)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         if request.method == 'DELETE':
#             subscr = get_object_or_404(Follow, user=follower, author=following)
#             subscr.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # @action(detail=True, methods=['GET'], url_path=f'(?P<user_id>\d+)')
    # def user(self, request):
    #     user = get_object_or_404(User, username=request.user)
    #     print(user)
    #     recipes = SubcriptionRecipeSerializer(id=user.id)
    #     serializer = SubscriptionGetSerializer()
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    # --------------------------------------------------------

# class UserFollowingViewSet(viewsets.ModelViewSet):

#     permission_classes = (IsAuthenticated,)
#     serializer_class = UserFollowSerializer
#     queryset = Follow.objects.all()
# --------------------------achive-------------------------------

 # @action(detail=False, methods=['GET'], url_path='favorites')
    # def favorites(self, request):
    #     print('hello')
    #     current_user = self.request.user
    #     if current_user.is_anonymous:
    #         return Response(status=status.HTTP_401_UNAUTHORIZED)
    #     favorites = current_user.favorite_recipes.all()
    #     serializer = FavoriteRecipeSerializer(favorites)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    # def get_queryset(self):
    #     print(self.context['request'].method)
    #     print(self.kwargs.get('id'))
    #     recipes_id = self.kwargs.get('id')
    #     recipes = get_object_or_404(Recipe, pk=recipes_id)
    #     queryset = recipes.favorite_recipes.all()
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



     # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user)

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     serializer = RecipeReadSerializer(instance=serializer.instance)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

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