from . import views
from rest_framework.routers import DefaultRouter
from django.conf.urls import include
from django.urls import path

router = DefaultRouter()
router.register(r'assets', views.AssetViewSet)
router.register(r'wallets', views.WalletViewSet)
router.register(r'contracts', views.ContractViewSet)
router.register(r'reports', views.ReportViewSet)
router.register(r'transactions', views.TransactionViewSet)

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'update-mask', views.update_mask),
    path(r'import-opensea', views.import_opensea),
]
