"""
RK Store — Django Admin Registration (Stage 3)
Lets you view and manage Products, Customers, and Orders
through the Django admin panel at /admin/
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Customer, Order, OrderItem


# ════════════════════════════════════════════════════════════════════════════
# PRODUCT ADMIN
# ════════════════════════════════════════════════════════════════════════════

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = [
        'name', 'storage', 'color', 'condition',
        'price', 'original_price', 'stock', 'stock_status_badge',
        'is_featured', 'is_special_offer', 'is_limited', 'is_active'
    ]
    list_filter   = ['condition', 'is_featured', 'is_latest',
                     'is_special_offer', 'is_limited', 'is_active']
    search_fields = ['name', 'color', 'storage']
    list_editable = ['stock', 'is_active']
    ordering      = ['name']

    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'storage', 'color', 'condition', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'original_price')
        }),
        ('Inventory', {
            'fields': ('stock', 'warranty', 'battery_health')
        }),
        ('Display Flags', {
            'fields': ('is_featured', 'is_latest', 'is_special_offer', 'is_limited', 'is_active'),
            'description': 'Control which sections of the homepage this product appears in.'
        }),
    )

    def stock_status_badge(self, obj):
        status = obj.stock_status
        colors = {
            'In Stock':    '#10B981',
            'Limited Stock': '#F59E0B',
            'Out of Stock':  '#EF4444',
        }
        color = colors.get(status, '#F59E0B')
        return format_html(
            '<span style="color:{};font-weight:600">{}</span>',
            color, status
        )
    stock_status_badge.short_description = 'Stock Status'


# ════════════════════════════════════════════════════════════════════════════
# ORDER ITEM INLINE (shown inside Order detail page)
# ════════════════════════════════════════════════════════════════════════════

class OrderItemInline(admin.TabularInline):
    model      = OrderItem
    extra      = 0
    readonly_fields = ['unit_price', 'line_total']

    def line_total(self, obj):
        return f"CAD ${obj.line_total:,.2f}"
    line_total.short_description = 'Line Total'


# ════════════════════════════════════════════════════════════════════════════
# ORDER ADMIN
# ════════════════════════════════════════════════════════════════════════════

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = [
        'order_number', 'customer', 'status',
        'total_amount', 'email_sent', 'sms_sent', 'created_at'
    ]
    list_filter   = ['status', 'email_sent', 'sms_sent']
    search_fields = ['order_number', 'customer__name', 'customer__email']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines       = [OrderItemInline]
    ordering      = ['-created_at']


# ════════════════════════════════════════════════════════════════════════════
# CUSTOMER ADMIN
# ════════════════════════════════════════════════════════════════════════════

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display  = ['name', 'email', 'phone', 'created_at']
    search_fields = ['name', 'email', 'phone']
    ordering      = ['-created_at']
