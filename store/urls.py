"""
RK Store — Store URL Routes (Stage 5)

Maps URLs to views. Think of this as the address book.
All these URLs are prefixed with /api/ from rk_store/urls.py

Full URL → View mapping:
    GET  /api/products/       → ProductListView
    GET  /api/products/1/     → ProductDetailView
    POST /api/orders/         → OrderCreateView
    GET  /api/orders/1/       → OrderDetailView
"""

from django.urls import path
from . import views

urlpatterns = [
    # Products
    path('products/',        views.ProductListView.as_view(),   name='product-list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),

    # Orders
    path('orders/',          views.OrderCreateView.as_view(),   name='order-create'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(),   name='order-detail'),
]
