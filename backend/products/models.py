from django.db import models

class Product(models.Model):
    product_id = models.CharField(max_length=50, unique=True, verbose_name="商品编号")
    name = models.CharField(max_length=200, verbose_name="商品名称")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="单价")
    stock_quantity = models.IntegerField(default=0, verbose_name="库存数量")
    description = models.TextField(blank=True, verbose_name="商品描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "商品"
        verbose_name_plural = "商品"
        ordering = ['product_id']

    def __str__(self):
        return f"{self.product_id} - {self.name}"