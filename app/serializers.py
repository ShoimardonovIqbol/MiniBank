from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    CustomerProfile, Wallet, BankCard, PaymentCategory, 
    ServiceProvider, Transaction, Payment, FavoritePayment, Notification
)
from datetime import datetime

# 1. Сериализатор для краткой информации о пользователе
class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

# 2. Сериализатор для Регистрации
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# 3. Сериализатор профиля клиента
class CustomerProfileSerializer(serializers.ModelSerializer):
    user_details = UserShortSerializer(source='user', read_only=True)

    class Meta:
        model = CustomerProfile
        fields = '__all__'

# 4. Сериализатор кошелька
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

# 5. Сериализатор банковской карты
class BankCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankCard
        fields = '__all__'

    def validate_expire_month(self, value):
        if not (1 <= value <= 12):
            raise serializers.ValidationError("Месяц должен быть от 1 до 12.")
        return value

    def validate_expire_year(self, value):
        if value < datetime.now().year:
            raise serializers.ValidationError("Год действия не может быть в прошлом.")
        return value

# 6. Сериализатор категории платежа
class PaymentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentCategory
        fields = '__all__'

# 7. Сериализатор провайдера услуг
class ServiceProviderSerializer(serializers.ModelSerializer):
    category_details = PaymentCategorySerializer(source='category', read_only=True)

    class Meta:
        model = ServiceProvider
        fields = '__all__'

# 8. Сериализатор транзакций
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

# 9. Сериализатор платежа
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

    def validate(self, attrs):
        wallet = attrs.get('wallet')
        amount = attrs.get('amount')
        if wallet and amount and wallet.balance < amount:
            raise serializers.ValidationError("На кошельке недостаточно средств.")
        return attrs

# 10. Сериализатор избранных платежей
class FavoritePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoritePayment
        fields = '__all__'

# 11. Сериализатор уведомлений
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

# 12. Вспомогательный сериализатор для перевода (Transfer)
class TransferSerializer(serializers.Serializer):
    sender_wallet_id = serializers.IntegerField()
    receiver_wallet_number = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)
