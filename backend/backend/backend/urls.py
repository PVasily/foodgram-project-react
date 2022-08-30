from django.contrib import admin
# from django.views.generic import TemplateView
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('recipes.urls'))
]
