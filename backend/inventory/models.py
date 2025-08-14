from django.db import models
from products.models import Product

class Customer(models.Model):
    name = models.CharField(max_length=200, verbose_name="客户名称")
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="联系人")
    phone = models.CharField(max_length=20, blank=True, verbose_name="联系电话")
    email = models.EmailField(blank=True, verbose_name="邮箱")
    address = models.TextField(blank=True, verbose_name="地址")
    remarks = models.TextField(blank=True, verbose_name="备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "客户"
        verbose_name_plural = "客户"
        ordering = ['name']
        
    def __str__(self):
        return self.name

class StoreInfo(models.Model):
    name = models.CharField(max_length=200, verbose_name="店铺名称")
    phone = models.CharField(max_length=20, verbose_name="联系电话")
    address = models.TextField(blank=True, verbose_name="地址")
    logo = models.ImageField(upload_to='logos/', blank=True, null=True, verbose_name="店铺Logo")
    remarks = models.TextField(blank=True, verbose_name="备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "店铺信息"
        verbose_name_plural = "店铺信息"
        
    def __str__(self):
        return self.name

class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('IN', '入库'),
        ('OUT', '出库'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="商品")
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="客户")
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES, verbose_name="操作类型")
    quantity = models.IntegerField(verbose_name="数量")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="单价")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="总价")
    transaction_date = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")
    remarks = models.TextField(blank=True, verbose_name="备注")
    
    # 新增字段
    document_number = models.CharField(max_length=50, blank=True, verbose_name="单据号码")  # 自动生成的时间戳单据号码
    preparer = models.CharField(max_length=50, blank=True, verbose_name="制单人")
    auditor = models.CharField(max_length=50, blank=True, verbose_name="审核人")
    handler = models.CharField(max_length=50, blank=True, verbose_name="经手人")
    receiver = models.CharField(max_length=50, blank=True, verbose_name="收货人")
    
    class Meta:
        verbose_name = "库存记录"
        verbose_name_plural = "库存记录"
        ordering = ['-transaction_date']

    def __str__(self):
        return f"{self.product.name} - {self.get_transaction_type_display()} - {self.quantity}"

    def save(self, *args, **kwargs):
        # 生成单据号码（时间戳格式）
        if not self.document_number:
            import time
            timestamp = str(int(time.time()))
            prefix = "RK" if self.transaction_type == "IN" else "CK"  # 入库单/出库单前缀
            self.document_number = f"{prefix}{timestamp}"
        
        # Calculate total price
        self.total_price = self.quantity * self.unit_price
        
        # Update product stock
        if not self.pk:  # Only when creating new transaction
            if self.transaction_type == 'IN':
                self.product.stock_quantity += self.quantity
            elif self.transaction_type == 'OUT':
                self.product.stock_quantity -= self.quantity
            self.product.save()
        
        super().save(*args, **kwargs)