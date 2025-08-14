from django.contrib import admin
from products.models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'name', 'price', 'stock_quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['product_id', 'name']
    ordering = ['product_id']