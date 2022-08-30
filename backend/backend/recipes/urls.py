from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CartViewset, DownloadCartListViewset, FavoriteViewSet,
                    IngredientViewset, ListCartViewSet, ListFavoriteViewSet,
                    RecipeViewset, SubscUserViewSet, TagViewset, UserMeViewset)

print('STEP 1')
router = DefaultRouter()

router.register('recipes', RecipeViewset)
router.register('ingredients', IngredientViewset)
router.register('users', UserMeViewset)
router.register('users', SubscUserViewSet)
router.register('tags', TagViewset)
router.register(r'recipes', CartViewset, basename='cart_list')
router.register(r'recipes', FavoriteViewSet, basename='favorite')
router.register(r'favorited', ListFavoriteViewSet, basename='favorited')
router.register(r'cart', ListCartViewSet, basename='list_cart')
router.register(r'', DownloadCartListViewset, basename='download')

app_name = 'recipes'

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.authtoken')),
]
