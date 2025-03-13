import datetime
from datetime import datetime, timedelta
import os
from django.http import HttpResponse
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from accounts.models import CompanyDetails
from .models import *
from .serializers import *
from .ai import generate_cover_letter_and_proposal, generate_recommendations_for_cover_letter_and_contract
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import textwrap
from django.core.mail import EmailMessage


API_KEY = settings.SAM_API_KEY


def get_contracts_details(NoticeID):
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
                return contract
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
        "limit": 20  
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
        return response.status_code

# -------------------------- ----------------


@api_view(['GET', 'POST'])
@permission_classes([])
def recent_contracts_list(request):
    keyword = request.data.get("keyword", "") if request.method == "POST" else ""

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

        contract = get_contracts_details(NOTICE_ID)
        description = get_contracts_description(NOTICE_ID)

        details = ContractDetails.objects.create(contract = contract, description = description)
        details.save()
        
        primary_contact = contract.get("pointOfContact", [{}])[0] 
        data =  {
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
            "description" : description,
        }
        return Response(data, status=status.HTTP_200_OK)
      
        



@api_view(["POST"])
def requirements_analysis(request):
    if request.method == "POST":
        try:
            notice_id = request.data.get('notice_id')
            contact_details = ContractDetails.objects.get(notice_id = notice_id)
            contact_details = contact_details.contract
            description = contact_details.description
            
            requirements = generate_recommendations_for_cover_letter_and_contract(description)

            RequirementsAnalysis.objects.create(
                notice_id = notice_id,
                user = request.user, 
                requirements = requirements
                )

            return Response({'requirements': requirements}, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        


@api_view(["POST"])
def generate_proposal(request):
    if request.method == "POST":
        try:
            notice_id = request.data.get('notice_id')
            contact_details = ContractDetails.objects.get(notice_id = notice_id)
            contact_details = contact_details.contract
            description = contact_details.description

            company_details = CompanyDetails.objects.get(user = request.user)
            proposal = generate_cover_letter_and_proposal(description, contact_details)  #ai function

            primary_contact = contact_details.get("pointOfContact", [{}])[0] 
            proposal_object = ContractProposal.objects.create(
                user = request.user,
                notice_id = notice_id,
                solicitation_number =  contact_details.get("solicitationNumber", None),
                title = contact_details.get("title", None),
                opportunity_type =  contact_details.get("type", None),
                inactive_date = contact_details.get("archiveDate", None),
                submit_email = primary_contact.get("email", None),
                submit_full_name = primary_contact.get("fullName", None),
                draft = False,
                proposal = proposal,
            )
            proposal_object.save()
            return Response({'proposal_id': proposal_object.id, 'proposal': proposal, 'notice_id': notice_id}, status=status.HTTP_200_OK)
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





def generate_pdf(text):
    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"generated_text_{current_datetime}.pdf"
    
    save_path = os.path.join(settings.MEDIA_ROOT, 'pdfs', filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    pdf = canvas.Canvas(save_path, pagesize=letter)
    width, height = letter
    margin = 50
    y_position = height - margin  # Start from top
    line_height = 15  # Space between lines
    max_width = width - (2 * margin)  # Usable width for text wrapping

    for line in text.split("\n"):
        wrapped_lines = textwrap.wrap(line, width=100)  # Wrap text to fit page
        for wrapped_line in wrapped_lines:
            pdf.drawString(margin, y_position, wrapped_line)
            y_position -= line_height
            if y_position < margin:  # If reaching bottom, create a new page
                pdf.showPage()
                y_position = height - margin

    relative_pdf_path = os.path.join('pdfs', filename)
    base_url = settings.BASE_URL 
    full_pdf_url = f"{base_url}/{relative_pdf_path}"

    pdf.save()
    print(save_path, full_pdf_url)
    return save_path



@api_view(['POST'])
@permission_classes([])   
def download_pdf(request):
    if request.method == "POST":
        proposal_id = request.data.get('proposal_id')

        if not proposal_id:
            return Response({'error': 'Proposal ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            contract_proposal = ContractProposal.objects.get(id=proposal_id)
        except ContractProposal.DoesNotExist:
            return Response({'error': 'Proposal not found.'}, status=status.HTTP_404_NOT_FOUND)

        proposal_text = contract_proposal.proposal
        if not proposal_text:
            return Response({'error': 'Proposal text is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        pdf_path = generate_pdf(text=proposal_text)

        contract_proposal.pdf_path = pdf_path
        contract_proposal.save()

        return Response({'message': 'PDF generated successfully.', 'pdf_path': pdf_path}, status=status.HTTP_200_OK)



        
@api_view(['POST'])
@permission_classes([])  
def send_pdf_email(request):
    if request.method == "POST":
        # Get the proposal_id from the request data
        proposal_id = request.data.get('proposal_id')
 
        if not proposal_id or not email:
            return Response({'error': 'Proposal ID and email are required.'}, status=400)
        
        try:
            # Retrieve the ContractProposal object
            contract_proposal = ContractProposal.objects.get(id=proposal_id)
        except ContractProposal.DoesNotExist:
            return Response({'error': 'Proposal not found.'}, status=404)

        # Generate PDF from the proposal text
        proposal_text = contract_proposal.proposal
        if not proposal_text:
            return Response({'error': 'Proposal text is empty.'}, status=400)

        # Generate the PDF
        pdf_path = generate_pdf(text=proposal_text)

        # Send email with PDF attachment
        subject = f"Response to Solicitation {contract_proposal.solicitation_number} – {contract_proposal.title}"
        message = 'Please find the contract proposal PDF attached.'
        email = contract_proposal.submit_email

        email_from = settings.EMAIL_HOST_USER 

        try:
            email_message = EmailMessage(
                subject=subject,
                body=message,
                from_email=email_from,
                to=[email],  
            )
            email_message.attach_file(pdf_path)
            email_message.send()

            return Response({'message': 'Email sent successfully with the PDF attachment.'}, status=200)
        
        except Exception as e:
            return Response({'error': f'Error sending email: {str(e)}'}, status=500)
        

        
@api_view(['POST'])
def send_email_link(request):
    proposal_id = request.data.get('proposal_id')

    contract_proposal = ContractProposal.objects.get(id = proposal_id)

    subject = f"Response to Solicitation {contract_proposal.solicitation_number} – {contract_proposal.title}"
    message = 'Please find the contract proposal PDF attached.'
    email = contract_proposal.submit_email

    email_link = f"mailto:{email}?subject={subject}&body={message}"

    return Response({'email_link': email_link}, status=status.HTTP_200_OK)