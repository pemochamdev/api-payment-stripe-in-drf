
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Customer {self.user.email}"

class PaymentMethod(models.Model):
    TYPES = (
        ('card', 'Carte bancaire'),
        ('sepa_debit', 'Prélèvement SEPA'),
        ('bancontact', 'Bancontact'),
        ('giropay', 'Giropay'),
        ('ideal', 'iDEAL'),
        ('p24', 'P24'),
        ('sofort', 'Sofort'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    stripe_payment_method_id = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPES)
    last4 = models.CharField(max_length=4, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('succeeded', 'Réussi'),
        ('failed', 'Échoué'),
        ('canceled', 'Annulé'),
        ('refunded', 'Remboursé'),
        ('partially_refunded', 'Partiellement remboursé'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Refund(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_refund_id = models.CharField(max_length=255, unique=True)
    reason = models.CharField(max_length=255)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

class Subscription(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20)
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

