from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *  # Ин ҷо '*' ҳама чизро аз views мегирад, то хатои ImportError нашавад

router = DefaultRouter()
router.register(r'profiles', CustomerProfileViewSet)
router.register(r'wallets', WalletViewSet)
router.register(r'cards', BankCardViewSet)
router.register(r'providers', ServiceProviderViewSet)
router.register(r'favorites', FavoritePaymentViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('payment-categories/', payment_category_list, name='payment-category-list'),
    path('transactions/', TransactionListAPIView.as_view(), name='transaction-list'),
    path('transactions/transfer/', TransferAPIView.as_view(), name='transaction-transfer'),
    path('payments/', PaymentListCreateAPIView.as_view(), name='payment-list-create'),
    path('notifications/<int:pk>/mark-as-read/', MarkNotificationAsReadAPIView.as_view(), name='mark-notification-read'),
]
