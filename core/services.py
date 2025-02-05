import stripe
from django.conf import settings
import stripe.error
from core.models import Customer,Payment,PaymentMethod,Refund,Subscription

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    
    @staticmethod
    def create_account(user, token=None):
        try:
            customer = stripe.Customer.create(
                email = user.email,
                source=token
            )
            
            return Customer.objects.create(
                user = user,
                stripe_customer_id = customer.id
            )
        except stripe.error.StripeError as e:
            raise Exception(f"Erreur lors de la création du client: {str(e)}")
    
    
    
    @staticmethod
    def add_payment_method(customer: Customer,payment_method_id):
        try:
            payment_method = stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer.stripe_customer_id
            )
            
            return PaymentMethod.objects.create(
                stripe_payment_method_id = payment_method.id,
                customer = customer,
                type = payment_method.type,
                last4 = payment_method.card.last4 if payment_method.type =="card" else None
            )
        except stripe.error.StripeError as e:
            raise Exception(f"Erreur lors de l'ajout du moyen de paiement: {str(e)}")
    
    
    @staticmethod
    def create_payment_intent(customer, amount, currency, payment_method_id=None):
        
        try:
            intent_params = {
                'amount': int(amount * 100),
                'currency': currency,
                'customer': customer.stripe_customer_id,
                'payment_method_types': ['card', 'sepa_debit', 'bancontact', 
                                       'giropay', 'ideal', 'p24', 'sofort'],
                'setup_future_usage': 'off_session',
            }
            
            if payment_method_id:
                intent_params['payment_method'] = payment_method_id
                
                intent = stripe.PaymentIntent.create(**intent_params)
                
                return Payment.objects.create(
                    customer=customer,
                    currency=currency,
                    stripe_payment_intent_id = intent.id
                    
                ), intent.client_secret
        except stripe.error.StripeError as e:
            raise Exception(f"Erreur lors de la création du paiement: {str(e)}")
    
    
    @staticmethod
    def process_refund(payment, amount=None, reason=None):
        try:
            refund_params = {
                'payment_intent': payment.stripe_payment_intent_id,
            }
            
            if amount:
                refund_params['amount'] = int(amount * 100)
            if reason:
                refund_params['reason'] = reason
                
            refund = stripe.Refund.create(**refund_params)
            
            return Refund.objects.create(
                payment=payment,
                amount=amount or payment.amount,
                stripe_refund_id=refund.id,
                reason=reason or 'requested_by_customer',
                status=refund.status
            )
            
        except stripe.error.StripeError as e:
            raise Exception(f"Erreur lors du remboursement: {str(e)}")
    
    
    @staticmethod
    def create_subscription(customer, price_id, payment_method_id=None):
        try:
            subscription = stripe.Subscription.create(
                customer=customer.stripe_customer_id,
                items=[{'price': price_id}],
                payment_method=payment_method_id,
                expand=['latest_invoice.payment_intent']
            )
            
            return Subscription.objects.create(
                customer=customer,
                stripe_subscription_id=subscription.id,
                status=subscription.status,
                current_period_start=subscription.current_period_start,
                current_period_end=subscription.current_period_end
            )
        except stripe.error.StripeError as e:
            raise Exception(f"Erreur lors de la création de l'abonnement: {str(e)}")