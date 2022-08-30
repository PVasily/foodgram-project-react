from core.filters import IngredientFilter, RecipeFilter
from core.permissions import IsAuthAndAuthorOrReadOnly
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from users.models import User
from users.serializers import UserSerializer

from .models import (Cart, Favorite, Follow, Ingredient, Recipe,
                     RecipeIngredient, Tag)
from .serializers import (IngredientSerializer, LightRecipeSerializer,
                          RecipeCreateSerializer, RecipeReadSerializer,
                          SubscriptionGetSerializer, SubscriptionSerializer,
                          TagSerializer, UserGetSerializer)


class CreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('pk')
    permission_classes = (IsAuthAndAuthorOrReadOnly, IsAdminUser,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', 'DELETE'):
            return RecipeCreateSerializer
        return RecipeReadSerializer


class IngredientViewset(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().order_by('pk')
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminUser,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = IngredientFilter


class TagViewset(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAdminUser,)


class CartViewset(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = LightRecipeSerializer
    permission_classes = (IsAuthenticated,)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk):
        current_user = self.request.user
        if current_user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe_in_favorite = Cart.objects.filter(
            user=current_user,
            recipe=recipe
        )
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
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthAndAuthorOrReadOnly,)

    def get_queryset(self):
        user = self.request.user
        return Recipe.objects.filter(cart_recipes__user=user)


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
    permission_classes = (IsAuthAndAuthorOrReadOnly,)

    @action(detail=True, methods=['POST', 'DELETE'], url_path='favorited')
    def favorited(self, request, pk):
        current_user = self.request.user
        if current_user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe_in_favorite = Favorite.objects.filter(
            user=current_user,
            recipe=recipe
        )
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
    permission_classes = (IsAuthAndAuthorOrReadOnly,)

    def get_queryset(self, ):
        user = self.request.user
        return Recipe.objects.filter(favorite_recipes__user=user)


class UserMeViewset(UserViewSet):
    queryset = User.objects.all()
    # serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SubscriptionSerializer
        return UserSerializer

    @action(
        detail=False,
        methods=['GET'],
        url_path='me'
    )
    def me(self, request):
        me = get_object_or_404(User, username=request.user)
        serializers = self.get_serializer(me)
        return Response(serializers.data, status=status.HTTP_200_OK)

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


class SubscUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserGetSerializer
    # pagination_class = PageNumberPagination
    # permission_classes = (IsAuthAndAuthorOrReadOnly,) #--?

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
            if not Follow.objects.filter(
                    user=follower,
                    author=following).exists():
                Follow.objects.create(user=follower, author=following)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        if request.method == 'DELETE':
            subscr = get_object_or_404(Follow, user=follower, author=following)
            subscr.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


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
#             subscr = get_object_or_404(
#                   Follow, user=follower,
#                   author=following
#             )
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

    # def perform_create(self, serializer):

    #     recipe_id = self.kwargs.get('id')
    #     recipe = get_object_or_404(Recipe, id=recipe_id)
    #     exist=Favorite.objects.filter(
    #         recipe=recipe,
    #         user=self.request.user,
    #         is_favorite=True
    #     ).exists()
    #     if self.request.user != recipe.author and exist != True:
    #         return Response(serializer.save(
    #                   user=self.request.user,
    #                   recipe=recipe,
    #                   is_favorite=True), status=status.HTTP_200_OK)
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
