import datetime
from datetime import datetime, timedelta
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from accounts.models import CompanyDetails
from .models import *
from .serializers import *
from .ai import generate_cover_letter_and_proposal
import requests


API_KEY = "9YcWOXkbXKd0cg6ExffTxiLEjgp3h1ZiHQIYdNej"




def get_contracts_details(NoticeID, all_data = False):
    BASE_URL = "https://api.sam.gov/opportunities/v2/search"

    today = datetime.today()
    one_year_ago = today - timedelta(days=364)

    posted_from = one_year_ago.strftime("%m/%d/%Y")
    posted_to = today.strftime("%m/%d/%Y")

    params = {
        "api_key": API_KEY,
        "postedFrom": posted_from,   
        "postedTo": posted_to,   
        "limit": 10  
    }

    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        
        for contract in data.get("opportunitiesData", []):
            if contract.get("noticeId") == NoticeID:
                if all_data:
                    return contract

                primary_contact = contract.get("pointOfContact", [{}])[0] 
                
                return {
                    "noticeId": contract.get("noticeId", 0),
                    "title": contract.get("title", 0),
                    "solicitationNumber": contract.get("solicitationNumber", 0),
                    "fullParentPathName": contract.get("fullParentPathName", 0),
                    "type": contract.get("type", 0),
                    "archiveDate": contract.get("archiveDate", 0),
                    "responseDeadLine": contract.get("responseDeadLine", 0),
                    "active": contract.get("active", 0),
                    "contact_email": primary_contact.get("email", None),
                    "contact_phone": primary_contact.get("phone", None),
                    "contact_fullName": primary_contact.get("fullName", None),
                }
    
    return None  




def get_contracts_list(keyword):
    BASE_URL = "https://api.sam.gov/opportunities/v2/search"
    

    today = datetime.today()
    one_year_ago = today - timedelta(days=364)

    posted_from = one_year_ago.strftime("%m/%d/%Y")
    posted_to = today.strftime("%m/%d/%Y")


    params = {
        "api_key": API_KEY,
        "keyword": keyword,  
        "postedFrom": posted_from,   
        "postedTo": posted_to,   
        "limit": 10  
    }

    # Make the request
    response = requests.get(BASE_URL, params=params)
    return response



def get_contracts_description(NOTICE_ID):
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
    


def fetch_contract_details(notice_id):
    url = f"https://api.sam.gov/prod/opportunities/v1/noticedesc?noticeid={notice_id}&api_key={API_KEY}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return f"❌ Error fetching contract {notice_id}: {response.status_code}"


#----------------


@api_view(['POST'])
@permission_classes([])
def recent_contracts_list(request):
    keyword = request.data.get("keyword")
    
    if not keyword:
        keyword = ""

    response = get_contracts_list(keyword)

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

        details = get_contracts_details(NOTICE_ID)
        data = get_contracts_description(NOTICE_ID)

        if data != "400":
            data['noticeId'] = details["noticeId"]
            data["title"] = details["title"]
            data["solicitationNumber"] = details["solicitationNumber"]
            data["fullParentPathName"] = details["fullParentPathName"]
            data["type"] = details["type"]
            data["archiveDate"] = details["archiveDate"]
            data["responseDeadLine"] = details["responseDeadLine"]
            data["active"] = details["active"]
            data["contact_email"] = details["contact_email"]
            data["contact_phone"] = details["contact_phone"]
            data["contact_fullName"] = details["contact_fullName"]

            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        



@api_view(["POST"])
def generate_proposal(request):
    if request.method == "POST":
        try:
            notice_id = request.data.get('notice_id')
            notice_details = get_contracts_details(NoticeID = notice_id , all_data = True)
            description = get_contracts_description(notice_id)
            company_details = CompanyDetails.objects.get(user = request.user)

            
            proposal = generate_cover_letter_and_proposal(description, notice_details)

            proposal_object = ContractProposal.objects.create(
                user = request.user,
                notice_id = notice_id,
                solicitation_number =  notice_details["solicitationNumber"],
                opportunity_type =  notice_details["type"],
                inactive_date = notice_details["archiveDate"],
                draft = False,
                proposal = proposal
            )
            proposal_object.save()

            return Response({'proposal': proposal}, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)



@api_view(["GET"])
def draf_proposal_list(request):
    if request.method == "GET":
        try:
            proposal_objects = ContractProposal.objects.filter(user = request.user, draft = True)
            serializers = ContractProposalSerializers(data = proposal_objects, many = True)
            return Response(serializers.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)



@api_view(["GET"])
def submit_proposal_list(request):
    if request.method == "GET":
        try:
            proposal_objects = ContractProposal.objects.filter(user = request.user, submit = True)
            serializers = ContractProposalSerializers(data = proposal_objects, many = True)
            return Response(serializers.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
def get_and_update_proposal_by_id(request):
        
    if request.method == "GET":
        try:
            proposal_id = request.data.get('proposal_id')
            
            proposal_object = ContractProposal.objects.get(id = proposal_id, user = request.user)
            proposal_object.save()

            return Response({'proposal': proposal_object.proposal}, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == "PUT":
        try:
            proposal_id = request.data.get('proposal_id')
            proposal = request.data.get('proposal')
            
            proposal_object = ContractProposal.objects.get(id = proposal_id, user = request.user)
            proposal_object.proposal = proposal
            proposal_object.save()

            return Response({'messages': "Proposal Updated"}, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([])
def apply_by_email(request):
    pass