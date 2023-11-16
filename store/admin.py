from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.db.models import Count
from django.http.request import HttpRequest
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models


class InventoryFilter(admin.SimpleListFilter):
    title = 'Inventory'
    parameter_name = 'inventory'
    
    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        return [
            ('<10', 'Low'),
            ('>10', 'OK')
            ]
        
    def queryset(self, request, queryset: QuerySet) -> QuerySet:
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)
        elif self.value() == '>10':
            return queryset.filter(inventory__gte=10)

class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    extra = 1
    readonly_fields = ['thumbnail']
    
    def thumbnail(self, instance):
        if instance.image.name != '':
            return format_html(f'<img src="{instance.image.url}" class="thumbnail" />')
        return ''

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ['title']
    }
    autocomplete_fields = ['collection']
    actions = ['clear_inventory']
    inlines = [ProductImageInline]
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    list_editable = ['unit_price']
    list_select_related = ['collection']
    list_filter = ['collection', 'last_update', InventoryFilter]
    list_per_page = 10
    search_fields = ['title']
    
    def collection_title(self, product):
        return product.collection.title
     
    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        else: return 'OK'

    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory = 0)
        self.message_user(request, f'{updated_count} products were succesfully updated.')
        
    class Media:
        css = {
            'all': ['store/styles.css']
        }
        
        
@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'orders_count']
    list_editable = ['membership']
    list_per_page = 20
    list_select_related = ['user']
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ['user__first_name__istartswith', 'user__last_name__istartswith']
    autocomplete_fields = ['user']
    
    @admin.display(ordering='ordercount')
    def orders_count(self, customer):
        url = (reverse('admin:store_order_changelist')
                + '?'
                + urlencode({
                    'customer__id': str(customer.id),
                })
               )
        return format_html('<a href={}>{}</a>',
                           url,
                           customer.ordercount)
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(
            ordercount = Count('order')
        )

class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    extra=1
    model = models.OrderItem
    
@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    list_display = ['id', 'placed_at', 'customer']
    
    
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    search_fields = ['title']
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(
            products_count = Count('products')
        )
    
    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = (reverse('admin:store_product_changelist')
               + '?'
               + urlencode({
                   'collection__id': str(collection.id),
               })
            )
        return format_html('<a href="{}"> {} </a>',
                           url,
                           collection.products_count)

    