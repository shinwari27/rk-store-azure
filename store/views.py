"""
RK Store — Views (Stage 5 + Stage 6)

Views handle all API requests.
Stage 6 adds automatic email + SMS notifications after order is placed.

Endpoints:
    GET  /api/products/        → list all active products
    GET  /api/products/<id>/   → single product detail
    POST /api/orders/          → place an order + send notifications
    GET  /api/orders/<id>/     → order detail
"""

import logging
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Product, Customer, Order, OrderItem
from .serializers import (
    ProductSerializer,
    OrderSerializer,
    OrderCreateSerializer,
)
from .notifications import send_order_notifications

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════
# PRODUCT VIEWS
# ════════════════════════════════════════════════════════════════════════════

class ProductListView(APIView):
    """
    GET /api/products/
    Returns all active products as JSON.
    Frontend uses this to display the catalog.
    """

    def get(self, request):
        products = Product.objects.filter(is_active=True)

        # Optional filters from query params
        condition = request.query_params.get('condition')
        if condition:
            products = products.filter(condition=condition)

        if request.query_params.get('featured') == 'true':
            products = products.filter(is_featured=True)

        if request.query_params.get('latest') == 'true':
            products = products.filter(is_latest=True)

        if request.query_params.get('special') == 'true':
            products = products.filter(is_special_offer=True)

        if request.query_params.get('limited') == 'true':
            products = products.filter(is_limited=True)

        serializer = ProductSerializer(products, many=True)
        return Response({
            'count':    products.count(),
            'products': serializer.data,
        })


class ProductDetailView(APIView):
    """
    GET /api/products/<id>/
    Returns a single product by ID.
    """

    def get(self, request, pk):
        try:
            product = Product.objects.get(id=pk, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductSerializer(product)
        return Response(serializer.data)


# ════════════════════════════════════════════════════════════════════════════
# ORDER VIEWS
# ════════════════════════════════════════════════════════════════════════════

class OrderCreateView(APIView):
    """
    POST /api/orders/
    Places a new order and sends email + SMS confirmation.

    Step by step:
        1. Validate all input data
        2. Check stock is available
        3. Create Customer record
        4. Create Order record
        5. Create OrderItem record
        6. Decrement product stock
        7. Send email + SMS notifications (Stage 6)
        8. Return order confirmation
    """

    def post(self, request):

        # Step 1 — Validate input
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        data    = serializer.validated_data
        product = data['product']

        try:
            with transaction.atomic():

                # Step 2 — Lock product row and re-check stock
                # select_for_update() prevents two simultaneous orders
                # from both buying the last unit
                product = Product.objects.select_for_update().get(id=product.id)

                if product.stock < data['quantity']:
                    return Response(
                        {'error': f'Only {product.stock} unit(s) in stock.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Step 3 — Create or get customer
                customer, _ = Customer.objects.get_or_create(
                    email=data['customer_email'],
                    defaults={
                        'name':    data['customer_name'],
                        'phone':   data['customer_phone'],
                        'address': data['customer_address'],
                    }
                )

                # Step 4 — Create order
                total = product.price * data['quantity']
                order = Order.objects.create(
                    customer=customer,
                    total_amount=total,
                    status=Order.CONFIRMED,
                )

                # Step 5 — Create order item
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=data['quantity'],
                    unit_price=product.price,
                )

                # Step 6 — Decrement stock
                product.stock -= data['quantity']
                product.save(update_fields=['stock'])

                logger.info(
                    f"Order {order.order_number} created — "
                    f"{product.name} x{data['quantity']} — "
                    f"CAD ${total} — {customer.email}"
                )

        except Exception as exc:
            logger.error(f"Order creation failed: {exc}")
            return Response(
                {'error': 'Order could not be processed. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Step 7 — Send email + SMS notifications
        # This runs OUTSIDE the transaction so a notification failure
        # never rolls back a valid order
        notifications = send_order_notifications(order, customer)

        # Step 8 — Return confirmation
        return Response(
            {
                'message':      'Order placed successfully.',
                'order_number': order.order_number,
                'total':        str(order.total_amount),
                'status':       order.status,
                'product':      product.name,
                'quantity':     data['quantity'],
                'customer':     customer.name,
                'email':        customer.email,
                'email_sent':   notifications['email_sent'],
                'sms_sent':     notifications['sms_sent'],
            },
            status=status.HTTP_201_CREATED
        )


class OrderDetailView(APIView):
    """
    GET /api/orders/<id>/
    Returns order details including all items.
    """

    def get(self, request, pk):
        try:
            order = Order.objects.get(id=pk)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderSerializer(order)
        return Response(serializer.data)
