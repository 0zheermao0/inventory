from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from inventory.models import InventoryTransaction
from inventory.serializers import InventoryTransactionSerializer, InventoryTransactionCreateSerializer
from inventory.report_utils import generate_inventory_report

class InventoryTransactionViewSet(viewsets.ModelViewSet):
    queryset = InventoryTransaction.objects.all()
    serializer_class = InventoryTransactionSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['product__product_id', 'product__name', 'remarks']
    filterset_fields = ['transaction_type', 'product__product_id', 'product__name']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InventoryTransactionCreateSerializer
        return InventoryTransactionSerializer
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        total_in = InventoryTransaction.objects.filter(transaction_type='IN').count()
        total_out = InventoryTransaction.objects.filter(transaction_type='OUT').count()
        return Response({
            'total_in': total_in,
            'total_out': total_out
        })
    
    @action(detail=False, methods=['get'])
    def print_report(self, request):
        # 获取选定的记录ID
        transaction_ids = request.GET.get('ids', None)
        
        if transaction_ids:
            # 如果提供了特定ID，则只打印这些记录
            ids = [int(id) for id in transaction_ids.split(',')]
            transactions = self.queryset.filter(id__in=ids)
        else:
            # 否则打印所有记录（根据筛选条件）
            transactions = self.filter_queryset(self.get_queryset())
            
        return generate_inventory_report(transactions, "inventory_transactions")