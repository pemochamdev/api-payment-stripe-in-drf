from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from core.models import Customer, PaymentMethod, Payment, Refund, Subscription
from core.serializers import (CustomerSerializer, PaymentMethodSerializer,
                         PaymentSerializer, RefundSerializer, SubscriptionSerializer)
from core.services import StripeService


class CustomerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSerializer
    
    def get_queryset(self):
        return Customer.objects.filter(user = self.request.user)
    
     
    @action(detail=True, methods=['post'])
    def add_payment_method(self, request, pk=None):
        customer = self.get_object()
        payment_method_id = request.data.get('payment_method_id')
        
        try:
            payment_method = StripeService.add_payment_method(
                customer=customer,
                payment_method_id=payment_method_id
            )
            serializer = PaymentMethodSerializer(payment_method)
            return ResourceWarning(serializer.data)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer
    
    def get_queryset(self):
        return Payment.objects.filter(customer__user = self.request.user)        
    
    def create(self, request):
        customer = get_object_or_404(Customer,user = request.user)
        amount = request.data.get('amount')
        currency = request.data.get('currency', "EUR")
        payment_method_id = request.data.get('payment_method_id')
        
        try:
            payment, client_secret = StripeService.create_payment_intent(
                customer,amount,currency,payment_method_id
            )
        
            return Response(
                {
                    "payment":PaymentSerializer(payment).data,
                    'client_secret':client_secret
                }
            )
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        payment = self.get_object()
        reason = request.data.get('reason')
        amount = request.data.get('amount')
        
        try:
            refund = StripeService.process_refund(
                payment,amount,reason
            )
            
            return Response(
                RefundSerializer(refund).data
            )
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class SubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer
    
    def get_queryset(self):
        return Subscription.objects.filter(customer__user=self.request.user)        
    
    
    def create(self, request):
        customer = get_object_or_404(Customer, user=request.user)
        price_id = request.data.get('price_id')
        payment_method_id = request.data.get('payment_method_id')
        
        try:
            subscription = StripeService.create_subscription(
                customer,price_id,payment_method_id
            )
            
            return Response(
                SubscriptionSerializer(subscription).data
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
