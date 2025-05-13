import datetime
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
import stripe
from .models import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscription_plan_list(request):
    if request.method == "GET":
        try:
            subscription_plans = SubscriptionPlan.objects.all()
            plans_data = [
            {
                "name": plan.name,
                "description": plan.description,
                "price": plan.price,
                "features": plan.features.split(",") if plan.features else [],
                "popular": plan.popular,
                "billing_cycle": "monthly" if int(plan.billing_cycle) <= 31 else "yearly",
            }
            for plan in subscription_plans
            ]
            return Response(plans_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def manage_subscription(request):
    if request.method == "GET":
        try:
            user = request.user
            subscription = Subscription.objects.filter(user=user).last()
            if subscription:
                subscription_data = {
                    "name": subscription.user.full_name,
                    "email": subscription.user.email,
                    "subscription_plan_name": subscription.plan.name,
                    "status": "active",
                    "purchase_date": subscription.start_date,
                    "expiry_date": subscription.start_date,
                }
                return Response(subscription_data, status=status.HTTP_200_OK)
            else:
                return Response({"message": "No subscription found"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    if request.method == "POST":
        try:
            user = request.user
            subscription = Subscription.objects.filter(user=user).last()
            if subscription:
                if subscription.status == True:
                    subscription.delete()
            return Response({"message": "Subscription cancle successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout_session(request):
    if request.method ==  "POST":
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            plan_id = request.data.get('plan_id')
        except Exception as e:
            return Response({"error": "Plan ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        plan = get_object_or_404(SubscriptionPlan, name=plan_id)

        try:
            price = stripe.Price.create(
                unit_amount=int(plan.price * 100),  # Convert price to cents
                currency="usd",
                recurring={
                    "interval": "day",  
                    "interval_count": plan.billing_cycle,  
                },
                product_data={"name": plan.name},
            )
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                mode='subscription',
                line_items=[{
                    'price': price.id,  
                    'quantity': 1,
                }],
                metadata={
                    'plan': plan.name,
                    'user_id': str(request.user.id)
                },
                success_url="http://192.168.10.131:8000/success/",  # Replace with production URL
                cancel_url="http://192.168.10.131:8000/cancel/",  # Replace with production URL
            )
            return Response({"session_id": session.id, "url": session.url}, status=status.HTTP_200_OK)
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@csrf_exempt
def stripe_webhook(request):
    try:
        print("Webhook triggered")
        payload = request.body
        sig_header = request.headers.get('Stripe-Signature', '')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        print(f"Event received: {event}")

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            metadata = session.get("metadata", {})
            plan_name = metadata.get("plan")
            user_id = metadata.get("user_id")

            if not plan_name or not user_id:
                print("Missing plan or user_id")
                return Response({"error": "Plan or user metadata missing"}, status=400)

            user = CustomUser.objects.filter(id=user_id).first()
            plan = SubscriptionPlan.objects.filter(name=plan_name).first()

            if not user or not plan:
                return Response({"error": "Invalid user or plan"}, status=400)
            
            subscription_id = session.get("subscription", "")
            
            stripe_subscription = stripe.Subscription.retrieve(subscription_id)
            end_date = datetime.utcfromtimestamp(stripe_subscription.current_period_end) 
            subscription, _ = Subscription.objects.get_or_create(
                                user=user, 
                                plan = plan, 
                                stripe_subscription_id = subscription_id,
                                status = True,
                                end_date = end_date,
                                next_payment_date = end_date,
                                )
            subscription.save()

            return Response({"message": "Subscription activated!"}, status=200)
        return Response({"message": "Unhandled event"}, status=400)

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return Response({"error": "Internal server error"}, status=500)