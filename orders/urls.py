# api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, RestauranteViewSet, OrdenViewSet

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet)
router.register(r'restaurantes', RestauranteViewSet)
router.register(r'ordenes', OrdenViewSet)

urlpatterns = [
    path('', include(router.urls)),
]