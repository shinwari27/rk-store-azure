"""
RK Store — Serializers (Stage 5)

Serializers convert between:
    Python objects (from database) ←→ JSON (for frontend)

Think of them as translators between Django and JavaScript.
"""

from rest_framework import serializers
from .models import Product, Customer, Order, OrderItem


# ════════════════════════════════════════════════════════════════════════════
# PRODUCT SERIALIZER
# Converts Product objects to JSON for the frontend
# ════════════════════════════════════════════════════════════════════════════

class ProductSerializer(serializers.ModelSerializer):

    # These are computed properties from models.py
    # We add them here so they appear in the JSON response
    stock_status    = serializers.ReadOnlyField()
    discount_amount = serializers.ReadOnlyField()
    is_in_stock     = serializers.ReadOnlyField()

    class Meta:
        model  = Product
        fields = [
            'id',
            'name',
            'storage',
            'color',
            'condition',
            'price',
            'original_price',
            'discount_amount',
            'stock',
            'stock_status',
            'is_in_stock',
            'warranty',
            'battery_health',
            'description',
            'is_featured',
            'is_latest',
            'is_special_offer',
            'is_limited',
            'is_active',
        ]


# ════════════════════════════════════════════════════════════════════════════
# ORDER ITEM SERIALIZER
# Represents one product line within an order
# ════════════════════════════════════════════════════════════════════════════

class OrderItemSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(source='product.name', read_only=True)
    line_total   = serializers.ReadOnlyField()

    class Meta:
        model  = OrderItem
        fields = [
            'id',
            'product',
            'product_name',
            'quantity',
            'unit_price',
            'line_total',
        ]


# ════════════════════════════════════════════════════════════════════════════
# ORDER SERIALIZER
# Used to READ order details (GET /api/orders/<id>/)
# ════════════════════════════════════════════════════════════════════════════

class OrderSerializer(serializers.ModelSerializer):

    items            = OrderItemSerializer(many=True, read_only=True)
    customer_name    = serializers.CharField(source='customer.name',    read_only=True)
    customer_email   = serializers.CharField(source='customer.email',   read_only=True)

    class Meta:
        model  = Order
        fields = [
            'id',
            'order_number',
            'customer_name',
            'customer_email',
            'status',
            'total_amount',
            'email_sent',
            'sms_sent',
            'items',
            'created_at',
        ]


# ════════════════════════════════════════════════════════════════════════════
# ORDER CREATE SERIALIZER
# Used to PLACE an order (POST /api/orders/)
# This is what the frontend sends when a customer clicks "Place Order"
# ════════════════════════════════════════════════════════════════════════════

class OrderCreateSerializer(serializers.Serializer):

    # Customer information (from order form)
    customer_name    = serializers.CharField(max_length=200)
    customer_email   = serializers.EmailField()
    customer_phone   = serializers.CharField(max_length=30)
    customer_address = serializers.CharField()

    # Product selection
    product_id = serializers.IntegerField()
    quantity   = serializers.IntegerField(min_value=1)

    def validate(self, data):
        """
        Check that:
        1. The product exists
        2. The product is active
        3. There is enough stock
        """
        try:
            product = Product.objects.get(id=data['product_id'], is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError({
                'product_id': 'Product not found or is no longer available.'
            })

        if product.stock < data['quantity']:
            raise serializers.ValidationError({
                'quantity': f'Only {product.stock} unit(s) available. You requested {data["quantity"]}.'
            })

        # Attach product object so view can use it without querying again
        data['product'] = product
        return data
