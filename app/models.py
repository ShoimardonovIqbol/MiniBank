from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20)
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField()
    passport_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} | {self.phone_number}"

class Wallet(models.Model):
    CURRENCY_CHOICES = [('TJS', 'TJS'), ('USD', 'USD'), ('RUB', 'RUB')]
    STATUS_CHOICES = [('ACTIVE', 'Active'), ('BLOCKED', 'Blocked'), ('CLOSED', 'Closed')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    wallet_number = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='TJS')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet: {self.wallet_number} ({self.user.username})"

class BankCard(models.Model):
    CARD_TYPES = [('VISA', 'Visa'), ('MASTERCARD', 'Mastercard'), ('KORTI_MILLI', 'Korti Milli'), ('OTHER', 'Other')]
    STATUS_CHOICES = [('ACTIVE', 'Active'), ('BLOCKED', 'Blocked'), ('EXPIRED', 'Expired')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards')
    card_holder = models.CharField(max_length=100)
    masked_pan = models.CharField(max_length=19)
    card_type = models.CharField(max_length=20, choices=CARD_TYPES)
    expire_month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    expire_year = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.card_type} | {self.masked_pan} ({self.user.username})"

class PaymentCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ServiceProvider(models.Model):
    category = models.ForeignKey(PaymentCategory, on_delete=models.CASCADE, related_name='providers')
    name = models.CharField(max_length=100)
    account_mask = models.CharField(max_length=100)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"

class Transaction(models.Model):
    TYPE_CHOICES = [('TOP_UP', 'Top Up'), ('TRANSFER', 'Transfer'), ('PAYMENT', 'Payment'), ('WITHDRAW', 'Withdraw')]
    STATUS_CHOICES = [('PENDING', 'Pending'), ('SUCCESS', 'Success'), ('FAILED', 'Failed'), ('CANCELLED', 'Cancelled')]
    sender_wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True, related_name='sent_transactions')
    receiver_wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True, related_name='received_transactions')
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    commission = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='TJS')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"TX {self.id}: {self.transaction_type} - {self.amount} {self.currency}"

class Payment(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pending'), ('SUCCESS', 'Success'), ('FAILED', 'Failed'), ('CANCELLED', 'Cancelled')]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    commission = models.DecimalField(max_digits=15, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment to {self.provider.name} | {self.amount} TJS"

class FavoritePayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"

class Notification(models.Model):
    TYPE_CHOICES = [('TRANSACTION', 'Transaction'), ('PAYMENT', 'Payment'), ('SYSTEM', 'System'), ('CARD', 'Card')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notify for {self.user.username}: {self.title}"
