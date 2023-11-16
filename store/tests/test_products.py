import pytest

from django.contrib.auth.models import User
from rest_framework import status

from model_bakery import baker

from store.models import Collection, Product


@pytest.mark.django_db
class TestCreateProduct:
    def test_if_user_anonymous_return_401(self, api_client):
        response = api_client.post('/store/products/', {"title": "test"})     
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_if_user_is_not_admin_returns_403(self, api_client, authenticate):
        # Arrange
        authenticate(is_staff=False)
        # Act
        response = api_client.post('/store/products/', {'title': 'test'})
        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        
    def test_if_data_is_invalid_returns_400(self, api_client):
        api_client.force_authenticate(user=User(is_staff=True))
        
        response = api_client.post('/store/products/', {"title": ""})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    
    def test_if_data_is_valid_returns_201(self, api_client):
        api_client.force_authenticate(user=User(is_staff=True))
        
        collection = Collection.objects.create(title="test")
        product_data = {
            "title": "Test Product",
            "description": "This is a test product.",
            "slug": "test-product",
            "inventory": 100,
            "unit_price": 10.0,
            "collection": collection.id
        }
        response = api_client.post('/store/products/', product_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0
       
       
       
@pytest.mark.django_db 
class TestRetrieveProducts:
    
    def if_product_exists_return_200(self, api_client):
        assert True