import datetime
from django.core.exceptions import ValidationError
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import *
from rest_framework.permissions import IsAuthenticated
import requests


API_KEY = "9YcWOXkbXKd0cg6ExffTxiLEjgp3h1ZiHQIYdNej"




def get_contracts_details(NOTICE_ID):
    BASE_URL = "https://api.sam.gov/prod/opportunities/v1/noticedesc"

    params = {
        "noticeid": NOTICE_ID,
        "api_key": API_KEY,
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return "400"




@api_view(['GET'])
@permission_classes([])
def contracts_list(request):

    BASE_URL = "https://api.sam.gov/opportunities/v2/search"
    from datetime import datetime, timedelta

    today = datetime.today()
    one_year_ago = today - timedelta(days=364)

    posted_from = one_year_ago.strftime("%m/%d/%Y")
    posted_to = today.strftime("%m/%d/%Y")


    params = {
        "api_key": API_KEY,
        "solicitationNumber": "W912EQ24B0007",
        "keyword": "software",  
        "postedFrom": posted_from,   
        "postedTo": posted_to,   
        "limit": 10  
    }

    # Make the request
    response = requests.get(BASE_URL, params=params)

    # Check for success
    if response.status_code == 2000:
        data = response.json()
        list_data = []
        for contract in data.get("opportunitiesData", []):
            list_data.append({
            "Title:", contract.get("title", "N/A"),
            "Solicitation Number:", contract.get("solicitationNumber", "N/A"),
            "Posted Date:", contract.get("postedDate", "N/A"),
            "Response Deadline:", contract.get("responseDeadLine", "N/A"),
            })
    else:
        print("Error:", response.status_code, response.text)

        return Response(data, status=status.HTTP_200_OK)
    return Response(response.text, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
@permission_classes([])
def contracts_details(request):
    if request.method == "POST":
        NOTICE_ID = request.data.get("notic_id")

        data = get_contracts_details(NOTICE_ID)
        if data != "400":
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        


@api_view(["POST", "PUT"])
def application(request):
    if request.method == "POST":
        pass

    if request.method == "PUT":
        pass


@api_view(['POST'])
@permission_classes([])
def apply_by_email(request):
    pass