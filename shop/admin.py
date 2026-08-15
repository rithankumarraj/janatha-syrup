from django.contrib import admin
from .models import (
    Category, Product, Review, Order, OrderItem,
    ContactMessage, NewsletterSubscriber, DeliveryOrder
)


# ─── Inlines ──────────────────────────────────────────────────────────
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'quantity', 'price', 'subtotal')

    def subtotal(self, obj):
        return f'₹{obj.subtotal}'


class DeliveryOrderItemInline(admin.TabularInline):
    """Read-only order items for delivery staff."""
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'quantity', 'price', 'subtotal')
    can_delete = False

    def subtotal(self, obj):
        return f'₹{obj.subtotal}'

    def has_add_permission(self, request, obj=None):
        return False


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('user', 'rating', 'comment', 'created_at')


# ─── Model Admins ────────────────────────────────────────────────────
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'product_count', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount_price', 'size', 'in_stock', 'featured', 'created_at')
    list_filter = ('category', 'in_stock', 'featured', 'size')
    list_editable = ('price', 'discount_price', 'in_stock', 'featured')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    inlines = [ReviewInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'phone', 'city', 'total', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    list_editable = ('status',)
    search_fields = ('order_number', 'full_name', 'email', 'phone', 'city', 'address')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'status', 'payment_method', 'total', 'notes')
        }),
        ('Customer Details', {
            'fields': ('user', 'full_name', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('address', 'city', 'state', 'pincode')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


# ─── Delivery Staff — Restricted Order Admin ─────────────────────────
@admin.register(DeliveryOrder)
class DeliveryOrderAdmin(admin.ModelAdmin):
    """
    Restricted admin for delivery staff.
    They can ONLY view orders and update the shipping status.
    No access to products, categories, users, or any other data.
    """
    list_display = ('order_number', 'full_name', 'phone', 'short_address', 'city', 'pincode', 'status', 'created_at')
    list_filter = ('status', 'city', 'created_at')
    list_editable = ('status',)
    search_fields = ('order_number', 'full_name', 'phone', 'city', 'address')
    readonly_fields = (
        'order_number', 'full_name', 'email', 'phone',
        'address', 'city', 'state', 'pincode',
        'total', 'payment_method', 'notes',
        'created_at', 'updated_at',
    )
    inlines = [DeliveryOrderItemInline]

    fieldsets = (
        ('Delivery Status', {
            'fields': ('status',),
            'description': 'Update the order status below.',
        }),
        ('Customer & Address', {
            'fields': ('full_name', 'phone', 'email', 'address', 'city', 'state', 'pincode'),
        }),
        ('Order Info', {
            'fields': ('order_number', 'total', 'payment_method', 'notes'),
            'classes': ('collapse',),
        }),
    )

    def short_address(self, obj):
        """Truncated address for list display."""
        return obj.address[:40] + '...' if len(obj.address) > 40 else obj.address
    short_address.short_description = 'Address'

    # Prevent delivery staff from adding or deleting orders
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    list_editable = ('is_read',)
    search_fields = ('name', 'email', 'subject', 'message')


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)


# ─── Admin Site Customization ────────────────────────────────────────
admin.site.site_header = '🍹 Janatha Syrup Administration'
admin.site.site_title = 'Janatha Syrup Admin'
admin.site.index_title = 'Manage Your Store'

