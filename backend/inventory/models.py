from django.db import models
from products.models import Product

class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('IN', '入库'),
        ('OUT', '出库'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="商品")
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES, verbose_name="操作类型")
    quantity = models.IntegerField(verbose_name="数量")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="单价")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="总价")
    transaction_date = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")
    remarks = models.TextField(blank=True, verbose_name="备注")
    
    class Meta:
        verbose_name = "库存记录"
        verbose_name_plural = "库存记录"
        ordering = ['-transaction_date']

    def __str__(self):
        return f"{self.product.name} - {self.get_transaction_type_display()} - {self.quantity}"

    def save(self, *args, **kwargs):
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