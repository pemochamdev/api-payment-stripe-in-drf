
from rest_framework import serializers
from core.models import Customer, PaymentMethod, Payment, Refund, Subscription

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'stripe_customer_id', 'created_at']

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'type', 'last4', 'is_default', 'created_at']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'currency', 'status', 'description', 
                 'metadata', 'created_at', 'updated_at']

class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ['id', 'payment', 'amount', 'reason', 'status', 'created_at']

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'status', 'current_period_start', 
                 'current_period_end', 'cancel_at_period_end']
