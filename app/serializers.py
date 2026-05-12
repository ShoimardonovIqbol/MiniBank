from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    CustomerProfile, Wallet, BankCard, PaymentCategory, 
    ServiceProvider, Transaction, Payment, FavoritePayment, Notification
)
from datetime import datetime

# 1. User Short Serializer (барои nested output)
class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

# 2. Customer Profile Serializer
class CustomerProfileSerializer(serializers.ModelSerializer):
    user_details = UserShortSerializer(source='user', read_only=True)

    class Meta:
        model = CustomerProfile
        fields = '__all__'

# 3. Wallet Serializer
class WalletSerializer(serializers.ModelSerializer):
    user_details = UserShortSerializer(source='user', read_only=True)

    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ['balance', 'wallet_number', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['balance'] = f"{instance.balance} {instance.currency}"
        return representation

# 4. Bank Card Serializer
class BankCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankCard
        fields = '__all__'

    def validate_expire_month(self, value):
        if not (1 <= value <= 12):
            raise serializers.ValidationError("Моҳ бояд аз 1 то 12 бошад.")
        return value

    def validate_expire_year(self, value):
        if value < datetime.now().year:
            raise serializers.ValidationError("Соли эътибор набояд гузашта бошад.")
        return value

# 5. Payment Category Serializer
class PaymentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentCategory
        fields = '__all__'

# 6. Service Provider Serializer
class ServiceProviderSerializer(serializers.ModelSerializer):
    category_details = PaymentCategorySerializer(source='category', read_only=True)

    class Meta:
        model = ServiceProvider
        fields = '__all__'

# 7. Transaction Serializer
class TransactionSerializer(serializers.ModelSerializer):
    sender_wallet_num = serializers.ReadOnlyField(source='sender_wallet.wallet_number')
    receiver_wallet_num = serializers.ReadOnlyField(source='receiver_wallet.wallet_number')

    class Meta:
        model = Transaction
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['amount'] = f"{instance.amount} {instance.currency}"
        return representation

# 8. Payment Serializer
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

    def validate(self, attrs):
        wallet = attrs.get('wallet')
        amount = attrs.get('amount')
        if wallet.balance < amount:
            raise serializers.ValidationError("Дар ҳамён маблағи кофӣ нест.")
        return attrs

# 9. Favorite Payment Serializer
class FavoritePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoritePayment
        fields = '__all__'

# 10. Notification Serializer
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

# --- Serializers барои Special Actions (POST-only) ---

class TopUpSerializer(serializers.Serializer):
    wallet_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)

class TransferSerializer(serializers.Serializer):
    sender_wallet_id = serializers.IntegerField()
    receiver_wallet_number = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)
