from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewset

app_name = 'users'

router = DefaultRouter()

router.register('users', UserViewset, basename='users_actions')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
