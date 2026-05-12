from rest_framework import viewsets, generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *

# ViewSets (CRUD-и стандартӣ)
class CustomerProfileViewSet(viewsets.ModelViewSet):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer

class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer

class ServiceProviderViewSet(viewsets.ModelViewSet):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer

class FavoritePaymentViewSet(viewsets.ModelViewSet):
    queryset = FavoritePayment.objects.all()
    serializer_class = FavoritePaymentSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

class BankCardViewSet(viewsets.ModelViewSet):
    queryset = BankCard.objects.all()
    serializer_class = BankCardSerializer

# FBV (Payment Categories)
@api_view(['GET', 'POST'])
def payment_category_list(request):
    if request.method == 'GET':
        categories = PaymentCategory.objects.all()
        serializer = PaymentCategorySerializer(categories, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = PaymentCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Generics
class TransactionListAPIView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class PaymentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

# APIViews барои мантиқи махсус
class TransferAPIView(APIView):
    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"status": "Success"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MarkNotificationAsReadAPIView(APIView):
    def patch(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk)
        notification.is_read = True
        notification.save()
        return Response({"status": "Read"})
