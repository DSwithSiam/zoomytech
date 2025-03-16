from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from stripe import Subscription


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
   
    otp = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()


class CompanyDetails(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='company_details')
    logo = models.ImageField(upload_to='logo/', blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)   
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(max_length=100, blank=True, null=True)   
    street = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    zipcode = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name if self.name else "Company Details"

