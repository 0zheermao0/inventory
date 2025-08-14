from rest_framework import serializers
from inventory.models import InventoryTransaction, Customer, StoreInfo
from products.models import Product
from products.serializers import ProductSerializer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class StoreInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreInfo
        fields = '__all__'

class InventoryTransactionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_id = serializers.CharField(source='product.product_id', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    
    class Meta:
        model = InventoryTransaction
        fields = '__all__'
        read_only_fields = ['total_price', 'document_number']

class InventoryTransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryTransaction
        fields = '__all__'
        read_only_fields = ['total_price', 'document_number']
        
    def validate(self, attrs):
        product = attrs['product']
        transaction_type = attrs['transaction_type']
        quantity = attrs['quantity']
        
        # For out transactions, check if there's enough stock
        if transaction_type == 'OUT' and product.stock_quantity < quantity:
            raise serializers.ValidationError(f"库存不足，当前库存：{product.stock_quantity}")
            
        attrs['unit_price'] = product.price
        return attrs