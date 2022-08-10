from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (RecipeViewset,
                   IngredientViewset,
                   UserViewset)

router = DefaultRouter()

router.register('recipes', RecipeViewset)
router.register('ingredients', IngredientViewset)
router.register('users', UserViewset)

app_name = 'recipes'

urlpatterns = [
    path('', include(router.urls)),
    path(r'auth/', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.jwt')),
]
