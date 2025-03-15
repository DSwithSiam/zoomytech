from django.contrib import admin
from .views import *
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(CompanyDetails)

