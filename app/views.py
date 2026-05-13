from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.serializers import Serializer
from rest_framework import serializers
from .models import *
from .serializers import *

# --- АУТЕНТИФИКАЦИЯ ---

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginRequestSerializer,
        responses={200: {'type': 'object'}}
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            return Response({"detail": "Шумо бомуваффақият ворид шудед."}, status=status.HTTP_200_OK)
        return Response({"detail": "Логин ё парол хато аст."}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"detail": "Шумо аз система баромадед."}, status=status.HTTP_200_OK)


# --- МОДЕЛҲОИ АСОСӢ (БЕХАТАРИИ МАҲДУД) ---

class CustomerProfileViewSet(viewsets.ModelViewSet):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer
    # Бе логин умуман дидан мумкин нест, чунки маълумоти шиноснома ҳаст
    permission_classes = [IsAuthenticated] 


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    # Баланси ҳамёнҳо набояд ба ҳама намоён бошад
    permission_classes = [IsAuthenticated] 


class BankCardViewSet(viewsets.ModelViewSet):
    queryset = BankCard.objects.all()
    serializer_class = BankCardSerializer
    # Рақами кортҳо бояд пӯшида бошад
    permission_classes = [IsAuthenticated]


# --- МОДЕЛҲОИ УМУМӢ (БЕ ЛОГИН ТАНҲО ДИДАН - READ ONLY) ---

class ServiceProviderViewSet(viewsets.ModelViewSet):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    
    def get_permissions(self):
        # Админ ҳама корро карда метавонад, бе логин танҳо дида метавонанд (GET)
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()] 
        return [IsAuthenticatedOrReadOnly()]


class FavoritePaymentViewSet(viewsets.ModelViewSet):
    queryset = FavoritePayment.objects.all()
    serializer_class = FavoritePaymentSerializer
    # Бе логин танҳо дидан (GET), бо логин сохтан (POST)
    permission_classes = [IsAuthenticatedOrReadOnly] 


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    # Бе логин танҳо дидан (GET)
    permission_classes = [IsAuthenticatedOrReadOnly]


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly]) # Ислоҳ шуд: бе логин танҳо GET кор мекунад
def payment_category_list(request):
    if request.method == 'GET':
        categories = PaymentCategory.objects.all()
        serializer = PaymentCategorySerializer(categories, many=True)
        return Response(serializer.data)
        
    elif request.method == 'POST':
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({"detail": "Танҳо админ метавонад созад."}, status=status.HTTP_403_FORBIDDEN)
        serializer = PaymentCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- ТРАНЗАКСИЯҲО ВА ПАРДОХТҲО (ҲАТМАН ЛОГИН ЛОЗИМ) ---

class TransactionListAPIView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]


class PaymentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]


class TransferAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=TransferSerializer,
        responses={200: TransactionSerializer}
    )
    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            amount = data['amount']
            sender_wallet = get_object_or_404(Wallet, id=data['sender_wallet_id'])
            receiver_wallet = get_object_or_404(Wallet, wallet_number=data['receiver_wallet_number'])

            if sender_wallet.balance < amount:
                return Response({"error": "Маблағи нокофӣ"}, status=status.HTTP_400_BAD_REQUEST)

            sender_wallet.balance -= amount
            receiver_wallet.balance += amount
            sender_wallet.save()
            receiver_wallet.save()

            transaction = Transaction.objects.create(
                sender_wallet=sender_wallet,
                receiver_wallet=receiver_wallet,
                transaction_type='TRANSFER',
                amount=amount,
                total_amount=amount,
                status='SUCCESS',
                description=data.get('description', '')
            )
            return Response(TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MarkNotificationAsReadAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({"status": "Read"})
