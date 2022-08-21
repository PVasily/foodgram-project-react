from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from .views import (CartViewset, CustomUserViewSet, FavoriteViewSet, RecipeViewset,
                    IngredientViewset, TagViewset, MainPageViewset,
                    )
from users.views import UserViewset

print('STEP 1')
router = DefaultRouter()

router.register('main', MainPageViewset)
router.register('recipes', RecipeViewset)
router.register('ingredients', IngredientViewset)
router.register('users', UserViewset)
router.register(r'users/subscriptions', CustomUserViewSet)
router.register(r'users/(?P<user_id>\d+)/subscribe', CustomUserViewSet, basename='subscribe')
router.register('tags', TagViewset)
# router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart', CartViewset)
router.register(r'recipes', CartViewset, basename='cart_list')
router.register(r'recipes', FavoriteViewSet, basename='list_favorite')


app_name = 'recipes'

urlpatterns = [
    path('', include(router.urls)),
    # path('api-token-auth/', views.obtain_auth_token),
    path(r'auth/', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.authtoken')),
    # path(r'auth/', include('djoser.urls.jwt')),
]
