from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.HelloView.as_view(), name='hello'),
    # path('hello/', views.say_hello, name='hello'),
]

