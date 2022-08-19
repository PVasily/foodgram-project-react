from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from .views import (CartViewset, RecipeViewset,
                    IngredientViewset, TagViewset, MainPageViewset,
                    )
from users.views import UserViewset

print('STEP 1')
router = DefaultRouter()

router.register('main', MainPageViewset)
router.register('recipes', RecipeViewset)
router.register('ingredients', IngredientViewset)
router.register('users', UserViewset)
# router.register(r'users/(?P<author_id>\d+)/subscribe', FollowViewset)
router.register('tags', TagViewset)
router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart', CartViewset)


app_name = 'recipes'

urlpatterns = [
    path('', include(router.urls)),
    # path('api-token-auth/', views.obtain_auth_token),
    path(r'auth/', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.authtoken')),
    # path(r'auth/', include('djoser.urls.jwt')),
]
