from django.shortcuts import get_list_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


from .serializers import (FollowSerializer, RecipeCreateSerializer,
                         RecipeReadSerializer, TagSerializer,
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
            return RecipeCreateSerializer
        return RecipeReadSerializer

    # def create(self, request, *args, **kwargs):
    #     data = request.data
    #     # ing = Ingredient.objects.get(id=data['ingredients'][0]['id'])
    #     # ai = AmountIngredient.objects.create(
    #     #                 ingredient=ing,
    #     #                 amount=data['ingredients'][0]['amount'])
    #     print(data)
    #     recipe = Recipe.objects.create(
    #                     name=data['name'],
    #                     image=data['image'],
    #                     author=request.user,
    #                     text=data['text'])
    #     recipe.save()
    #     print(recipe)
    #     for tag in data['tags']:
    #         tag_obj = Tag.objects.get(id=tag)
    #         tag_obj = tag_obj.id
    #         recipe.tags.add(tag_obj)
    #     for ing in data['ingredients']:
    #         # need AmountIngredient
    #         ing_obj = Ingredient.objects.get(id=ing['id'])
    #         f = {"id": ing_obj.id, "amount": ing['amount']}
    #         ing_obj.add(amount=ing['amount'])
    #         print(f)
    #         print(ing['amount'])
    #         recipe.ingredients.add(ing_obj)
    #     sesrializer = RecipeCreateSerializer(recipe)
    #     return Response(sesrializer.data)


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
