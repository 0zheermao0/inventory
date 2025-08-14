from django.urls import path, include
from rest_framework.routers import DefaultRouter
from products.views import ProductViewSet
from inventory.views import InventoryTransactionViewSet
from inventory.test_chinese import test_chinese_pdf_cids

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'inventory-transactions', InventoryTransactionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/test-chinese-pdf/', test_chinese_pdf_cids),
]