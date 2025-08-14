from django.db import models

class Product(models.Model):
    product_id = models.CharField(max_length=50, unique=True, verbose_name="商品编号")
    name = models.CharField(max_length=200, verbose_name="商品名称")
    specification = models.CharField(max_length=100, blank=True, verbose_name="规格")  # 新增规格字段
    unit = models.CharField(max_length=20, blank=True, verbose_name="单位")  # 新增单位字段
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
        spec_unit = ""
        if self.specification:
            spec_unit += f" {self.specification}"
        if self.unit:
            spec_unit += f"/{self.unit}"
        return f"{self.product_id} - {self.name}{spec_unit}"