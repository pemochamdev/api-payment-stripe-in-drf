import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from core.models import Payment, Subscription

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
        
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        payment = Payment.objects.filter(
            stripe_payment_intent_id=payment_intent.id
        ).first()
        if payment:
            payment.status = 'succeeded'
            payment.save()
            
    elif event.type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        payment = Payment.objects.filter(
            stripe_payment_intent_id=payment_intent.id
        ).first()
        if payment:
            payment.status = 'failed'
            payment.save()
            
    elif event.type == 'customer.subscription.updated':
        subscription = event.data.object
        local_subscription = Subscription.objects.filter(
            stripe_subscription_id=subscription.id
        ).first()
        if local_subscription:
            local_subscription.status = subscription.status
            local_subscription.current_period_end = subscription.current_period_end
            local_subscription.save()
    
    return HttpResponse(status=200)
