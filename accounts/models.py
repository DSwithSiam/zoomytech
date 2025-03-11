from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):
    def create_superuser(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, is_staff=True, is_superuser=True, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, blank=True, null=True) 
    full_name = models.CharField(max_length=50, blank=True, null=True, default="")
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to='users_images/', blank=True, null=True)
    subscription_plan = models.BooleanField(default=False)
  
    
    otp = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    # EMAIL_FIELD = "email" 
    objects = CustomUserManager()