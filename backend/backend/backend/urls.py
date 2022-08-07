from django.contrib import admin
# from django.views.generic import TemplateView
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('redoc/', TemplateView.as_view(
    #     template_name='docs/redoc.html',
    #     extra_context={'schema_url':'openapi-schema'}
    # ), name='redoc'),
]
