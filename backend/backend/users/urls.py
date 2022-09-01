from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewset

app_name = 'users'

router = DefaultRouter()

router.register('users', UserViewset)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.authtoken')),
]
