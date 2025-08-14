from django.contrib import admin
from inventory.models import InventoryTransaction

@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ['product', 'transaction_type', 'quantity', 'unit_price', 'total_price', 'transaction_date']
    list_filter = ['transaction_type', 'transaction_date']
    search_fields = ['product__product_id', 'product__name']
    ordering = ['-transaction_date']
    readonly_fields = ['total_price', 'transaction_date']