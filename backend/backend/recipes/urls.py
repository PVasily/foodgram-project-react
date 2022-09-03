from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewset, ListCartViewSet, ListFavoriteViewSet,
                    RecipeViewset, TagViewset)

app_name = 'recipes'

router = DefaultRouter()

router.register('recipes', RecipeViewset)
router.register('ingredients', IngredientViewset)
router.register('tags', TagViewset)
router.register('favorited', ListFavoriteViewSet, basename='favorited')
router.register('cart', ListCartViewSet, basename='list_cart')

urlpatterns = [
    path('', include(router.urls)),
]
