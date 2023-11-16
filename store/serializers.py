from decimal import Decimal
from django.db import transaction
from rest_framework import serializers

from .signals import order_created
from store.models import Product, Collection, Review, Cart, CartItem, Customer, Order, OrderItem, ProductImage

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']
    products_count = serializers.IntegerField(read_only=True) # annotated column coming in this

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']
        
    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 
                  'price_with_tax', 'collection', 'images']

    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    
    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)
    
    def validate(self, attrs):
        # Just showing how to override with an example
        # if attrs['password'] != attrs['confirm_password']:
        #     return serializers.ValidationError('Password Do not Match.')
        return super().validate(attrs)
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']
        
    def create(self, validated_data):
        product_id = self.context['product_id']
        newReview = Review.objects.create(product_id = product_id, **validated_data)
        return newReview
        

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']        


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(method_name='get_total_price')

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']
        
    def get_total_price(self, instance: Cart):
        return sum([item.quantity * item.product.unit_price for item in instance.items.all()])
    
    
class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']
        
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with the given ID was found')
        return value
    
    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
         
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        
        return self.instance
    
    
class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']
        
        
class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']
        
        
class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    # total_price = serializers.SerializerMethodField(method_name='get_total_price')
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']
    # def get_total_price(self, orderitem):
    #     return orderitem.quantity * ( orderitem.unit_price)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items']
        
        
class CreateOrderSerializer(serializers.ModelSerializer):
    cart_id = serializers.UUIDField()

    class Meta:
        model = Order
        fields = ['cart_id']
        
    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('No cart with the given ID was found.')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The cart is empty.')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            customer = Customer.objects.get(user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer)
            items = CartItem.objects \
                            .select_related('product') \
                            .filter(cart_id=self.validated_data['cart_id'])
            order_items = []
            for item in items:
                order_items.append(
                    OrderItem(
                        order = order,
                        product = item.product,
                        unit_price = item.product.unit_price,
                        quantity = item.quantity
                    ))   
            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(pk=self.validated_data['cart_id']).delete()
            
            order_created.send_robust(sender=self.__class__, order=order)
            
            return order
        
class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']
