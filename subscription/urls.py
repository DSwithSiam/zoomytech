from django.urls import path
from .views import *

urlpatterns = [
    path('plan/list/', subscription_plan_list, name='subscription-plan-list'),
    path('manage/', manage_subscription, name = 'manage_subscription'),

    path('checkout-session/', checkout_session, name='checkout-session'),
    path('webhook/', stripe_webhook, name='webhook'),
]

