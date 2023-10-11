from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('collections', views.CollectionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # path('products/', views.ProductList.as_view()), and more as per ur need
]
