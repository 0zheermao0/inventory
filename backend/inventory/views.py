from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from inventory.models import InventoryTransaction, Customer, StoreInfo
from inventory.serializers import InventoryTransactionSerializer, InventoryTransactionCreateSerializer, CustomerSerializer, StoreInfoSerializer
from inventory.report_utils import generate_inventory_report
from django.db.models import Q

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'contact_person', 'phone']
    filterset_fields = ['name']

class StoreInfoViewSet(viewsets.ModelViewSet):
    queryset = StoreInfo.objects.all()
    serializer_class = StoreInfoSerializer

class InventoryTransactionViewSet(viewsets.ModelViewSet):
    queryset = InventoryTransaction.objects.all()
    serializer_class = InventoryTransactionSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['product__product_id', 'product__name', 'remarks', 'customer__name', 'document_number']
    filterset_fields = ['transaction_type', 'product__product_id', 'product__name', 'customer']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InventoryTransactionCreateSerializer
        return InventoryTransactionSerializer
    
    def get_queryset(self):
        queryset = InventoryTransaction.objects.all()
        # 添加日期范围过滤
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        customer = self.request.query_params.get('customer', None)
        
        if date_from:
            queryset = queryset.filter(transaction_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(transaction_date__lte=date_to)
        if customer:
            queryset = queryset.filter(customer=customer)
            
        return queryset
    
    def perform_create(self, serializer):
        # 在创建时保存额外的字段
        serializer.save(
            preparer=self.request.data.get('preparer', ''),
            auditor=self.request.data.get('auditor', ''),
            handler=self.request.data.get('handler', ''),
            receiver=self.request.data.get('receiver', '')
        )
    
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
        # 获取纸张规格参数
        paper_size = request.GET.get('paper_size', 'A4')
        
        if transaction_ids:
            # 如果提供了特定ID，则只打印这些记录
            ids = [int(id) for id in transaction_ids.split(',')]
            transactions = self.queryset.filter(id__in=ids)
        else:
            # 否则打印所有记录（根据筛选条件）
            transactions = self.filter_queryset(self.get_queryset())
            
        return generate_inventory_report(transactions, "inventory_transactions", paper_size)