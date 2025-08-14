from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse, FileResponse
from django.conf import settings
import os
from inventory.models import InventoryTransaction, TransactionItem, Customer, StoreInfo
from inventory.serializers import InventoryTransactionSerializer, InventoryTransactionCreateSerializer, CustomerSerializer, StoreInfoSerializer
from inventory.report_utils import generate_inventory_report
from inventory.excel_utils import (
    export_products_to_excel, import_products_from_excel,
    export_customers_to_excel, import_customers_from_excel,
    export_inventory_transactions_to_excel, import_inventory_transactions_from_excel
)
from django.db.models import Q
import pandas as pd

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
    search_fields = ['document_number', 'remarks', 'customer__name']
    filterset_fields = ['transaction_type', 'customer']
    
    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
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
    
    @action(detail=False, methods=['get'])
    def export_products(self, request):
        """导出商品信息到Excel"""
        return export_products_to_excel()
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def import_products(self, request):
        """从Excel导入商品信息"""
        file = request.FILES.get('file')
        if not file:
            return Response({'error': '未提供文件'}, status=400)
        
        try:
            result = import_products_from_excel(file)
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
    
    @action(detail=False, methods=['get'])
    def export_customers(self, request):
        """导出客户资料到Excel"""
        return export_customers_to_excel()
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def import_customers(self, request):
        """从Excel导入客户资料"""
        file = request.FILES.get('file')
        if not file:
            return Response({'error': '未提供文件'}, status=400)
        
        try:
            result = import_customers_from_excel(file)
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
    
    @action(detail=False, methods=['get'])
    def export_transactions(self, request):
        """导出入库订单到Excel"""
        return export_inventory_transactions_to_excel()
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def import_transactions(self, request):
        """从Excel导入出入库订单"""
        file = request.FILES.get('file')
        if not file:
            return Response({'error': '未提供文件'}, status=400)
        
        try:
            result = import_inventory_transactions_from_excel(file)
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
    
    @action(detail=False, methods=['get'])
    def download_product_template(self, request):
        """下载商品信息模板"""
        template_path = os.path.join(settings.BASE_DIR, 'static', 'templates', 'products_template.xlsx')
        if os.path.exists(template_path):
            response = FileResponse(open(template_path, 'rb'), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="products_template.xlsx"'
            return response
        else:
            return Response({'error': '模板文件不存在'}, status=404)
    
    @action(detail=False, methods=['get'])
    def download_customer_template(self, request):
        """下载客户资料模板"""
        template_path = os.path.join(settings.BASE_DIR, 'static', 'templates', 'customers_template.xlsx')
        if os.path.exists(template_path):
            response = FileResponse(open(template_path, 'rb'), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="customers_template.xlsx"'
            return response
        else:
            return Response({'error': '模板文件不存在'}, status=404)
    
    @action(detail=False, methods=['get'])
    def download_transaction_template(self, request):
        """下载出入库订单模板"""
        template_path = os.path.join(settings.BASE_DIR, 'static', 'templates', 'transactions_template.xlsx')
        if os.path.exists(template_path):
            response = FileResponse(open(template_path, 'rb'), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="transactions_template.xlsx"'
            return response
        else:
            return Response({'error': '模板文件不存在'}, status=404)