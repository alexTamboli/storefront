from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from .models import Product, Collection, Review
from .serializers import ProductSerializer, CollectionSerializer, ReviewSerializer
from .filters import ProductFilter


class ProductViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    
    def get_queryset(self):
        return Product.objects.all()
    
    def get_serializer_class(self):
        return ProductSerializer
    
    def get_serializer_context(self):
        context = {"request": self.request}
        return context
    
    def destroy(self, request, pk):
        product = self.get_object()
        if product.orderitems.count() > 0:
            return Response({
                "error": "product cannot be deleted it is associated with an orderitem."
            }, status=status.HTTP_405_METHOD_NOT_ALLOWED )
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count = Count('products')).all()
    serializer_class = CollectionSerializer
    
    def destroy(self, request, pk):
        collection = self.get_object()
        if collection.products_count > 0:
            return Response({"error": "Collection cannot be deleted as it is associated with one or more products"}, 
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        return Review.objects.filter(product_id = self.kwargs['product_pk'])
    
    def get_serializer_context(self):
        return {"product_id": self.kwargs['product_pk']}  