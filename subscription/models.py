from django.db import models

from accounts.models import CustomUser

# Create your models here.

class Offers(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    features = models.TextField(blank=True, null=True)  # Comma-separated values
    stripe_price_id = models.CharField(max_length=255) 
    price = models.DecimalField(max_digits=10, decimal_places=2)
    popular = models.BooleanField(default=False)  # To mark if the plan is popular
    billing_cycle = models.CharField(max_length=100)  #  "monthly", "annually"
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name



class Subscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=255)  # Stripe's subscription ID
    status = models.BooleanField(default=False)  # Active or inactive
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)  # To track when the subscription ends
    next_payment_date = models.DateTimeField(blank=True, null=True)  # When next payment is due

    def __str__(self):
        return f'{self.user.username} - {self.plan.name}'
