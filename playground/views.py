from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F, Value, Func, ExpressionWrapper, DecimalField
from django.db.models.aggregates import Count, Max, Min, Avg, Sum
from django.contrib.contenttypes.models import ContentType

from store.models import Collection, Product, OrderItem, Order, Customer
from tags.models import TaggedItem


# Create your views here.
def say_hello(request):
    # queryset = Product.objects.raw("SELECT id, title FROM store_product ORDER BY title")

    # collection = Collection()
    # collection.title = 'test 2'
    # collection.featured_product = Product(pk=2)
    # collection.save()
    
    # collection = Collection.objects.create(title='Video Games', featured_product=Product.objects.get(pk=1))
    context = {
        'name': 'Alex',
        # 'products': list(queryset),
    }
    return render(request, 'hello.html', context)
