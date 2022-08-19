from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination

from users.models import User


from .serializers import (CartReadSerializer, CartRecipeWriteSerializer, RecipeCreateSerializer,
                         RecipeReadSerializer, TagSerializer,
                         IngredientSerializer,
                         TagSerializer)
from .models import Cart, Follow, Recipe, Ingredient, Tag


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


class IngredientViewset(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().order_by('pk')
    serializer_class = IngredientSerializer


class TagViewset(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer


class CartViewset(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartRecipeWriteSerializer
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CartReadSerializer
        return CartRecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if request.method == 'GET':
            recipes = get_object_or_404(Recipe, author=request.user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = CartRecipeWriteSerializer(instance=serializer.instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


        # for recipe in recipes:
        # return super().create(request, *args, **kwargs)

    # def get_queryset(self):
    #     return super().get_queryset()


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
