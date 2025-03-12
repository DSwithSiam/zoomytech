
from django.urls import path
from .views import *

urlpatterns = [
    path('recent/list/', recent_contracts_list, name = "recent_contracts_list"),
    path('details/', contracts_details, name = "contracts_details"),
]

