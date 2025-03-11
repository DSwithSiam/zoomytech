
from django.urls import path
from .views import *

urlpatterns = [
    path('list/', contracts_list, name = "contracts_list"),
    path('details/', contracts_details, name = "contracts_details"),
]

