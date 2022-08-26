from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from .views import (CartViewset, DownloadCartListViewset, FavoriteViewSet, 
                    ListCartViewSet, ListFavoriteViewSet, ProfileViewset,
                    RecipeViewset,
                    IngredientViewset, SubscUserViewSet,
                    TagViewset,
                    # MainPageViewset,
                    UserViewset
                    )
# from users.views import UserViewset

print('STEP 1')
router = DefaultRouter()

# router.register('', MainPageViewset)
router.register('recipes', RecipeViewset)
router.register('ingredients', IngredientViewset)
router.register('users', UserViewset)
# router.register(r'users', SubscUserViewSet)
# router.register(r'users', ProfileViewset, basename='profile')
router.register('users', SubscUserViewSet, basename='subscribe')
router.register('tags', TagViewset)
# router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart', CartViewset)
router.register(r'recipes', CartViewset, basename='cart_list')
router.register(r'recipes', FavoriteViewSet, basename='favorite')
router.register(r'favorited', ListFavoriteViewSet, basename='favorited')
router.register(r'recipe/shopping_cart', ListCartViewSet, basename='list_cart')
router.register(r'recipe', DownloadCartListViewset, basename='download')

app_name = 'recipes'

urlpatterns = [
    path('', include(router.urls)),
    path(r'auth/', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.authtoken')),
    # path(r'auth/', include('djoser.urls.jwt')),
]

# path('api-token-auth/', views.obtain_auth_token),