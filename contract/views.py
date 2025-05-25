import datetime
from datetime import datetime, timedelta
import json
import os
from django.http import HttpResponse
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from accounts.models import CompanyDetails
from contract.utils import remove_extra_c
from .models import *
from .serializers import *
from .ai import *
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile


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
    print(response, "--------------------------")
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
        "limit": 5 
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
        if "description" in data:
            return data
        else:
            return {"description": "Description Not Found"}
    else:
        return {"description": "Description Not Found"}
    


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
    if response.status_code == 200:
        all_data = response.json()
        data = []
        for contract in all_data.get("opportunitiesData", []):
            print(contract, "--------------------------")
            
            data.append({
            "Title" : contract.get("title", "N/A"),
            "noticeId" : contract.get("noticeId", "N/A"),
            "Solicitation Number": contract.get("solicitationNumber", "N/A"),
            "Posted Date": contract.get("postedDate", "N/A"),
            "Response Deadline": contract.get("responseDeadLine", "N/A"),
            })
            
        return Response(data, status=status.HTTP_200_OK)
    return Response(response.text, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
@permission_classes([])
def contracts_details(request, notice_id):
    if request.method == "GET":
        NOTICE_ID = notice_id
        contract = get_contracts_details(NOTICE_ID)
        description = get_contracts_description(NOTICE_ID)
        print(description, "--------------------------")
        try:
            contract_details = ContractDetails.objects.filter(notice_id=NOTICE_ID).exists()
            if not contract_details:
                details = ContractDetails.objects.create(
                    notice_id = NOTICE_ID,
                    contract = contract, 
                    description =  description['description']
                    )
                details.save()
        except:
            return Response( status=status.HTTP_400_BAD_REQUEST)
        print(contract, "--------------------------")
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
            "description" : description["description"],
        }
        return Response(data, status=status.HTTP_200_OK)
      
        



@api_view(["POST"])
def requirements_analysis(request):
    if request.method == "POST":
        notice_id = request.data.get('notice_id')
        try:
            contact_details = ContractDetails.objects.get(notice_id=notice_id)
        except ContractDetails.DoesNotExist:
            return Response({"message": "Contract Details not found"}, status=status.HTTP_404_NOT_FOUND)
        contact_details = contact_details.contract
        description = contact_details["description"]
        
        # requirements = generate_recommendations_for_cover_letter_and_contract(description)
        requirements = generate_recommendations_for_cover_letter_and_contract(description)
        
        requirements = remove_extra_c(requirements)
        RequirementsAnalysis.objects.create(
            notice_id = notice_id,
            user = request.user, 
            requirements = requirements
            )

        return Response(requirements, status=status.HTTP_200_OK)
        # except:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)
        

@api_view(["POST"])
def generate_proposal(request):
    if request.method == "POST":
        try:
            notice_id = request.data.get('notice_id')
            budget = request.data.get('amount')

            if not notice_id:
                return Response({'error': 'Notice ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

            contact_details_obj = ContractDetails.objects.get(notice_id=notice_id)
            description = contact_details_obj.description
            contract_data = contact_details_obj.contract

            company_obj = getattr(request.user, 'company_details', None)

            if not company_obj:
                company_details = {
                    "name": request.user.full_name,
                    "email": request.user.email,
                    "phone": None,
                    "website": None,
                    "street": None,
                    "city": None,
                    "zipcode": None,
                    "state": None,
                }
            else:
                company_details = {
                    "name": company_obj.name,
                    "email": company_obj.email,
                    "phone": company_obj.phone,
                    "website": company_obj.website,
                    "street": company_obj.street,
                    "city": company_obj.city,
                    "zipcode": company_obj.zipcode,
                    "state": company_obj.state,
                }

            proposal = generate_cover_letter_and_proposal(description, contract_data, company_details, budget)

            primary_contact = contract_data.get("pointOfContact", [{}])[0]
            proposal = remove_extra_c(proposal)
            proposal_object = ContractProposal.objects.create(
                user=request.user,
                notice_id=notice_id,
                solicitation_number=contract_data.get("solicitationNumber"),
                title=contract_data.get("title"),
                opportunity_type=contract_data.get("type"),
                inactive_date=contract_data.get("archiveDate"),
                submit_email=primary_contact.get("email"),
                submit_full_name=primary_contact.get("fullName"),
                draft=False,
                proposal=proposal,
            )

            return Response({
                'proposal_id': proposal_object.id,
                'proposal': proposal,
                'notice_id': notice_id
            }, status=status.HTTP_200_OK)

        except ContractDetails.DoesNotExist:
            return Response({'message': 'Contract details not found.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



@api_view(["POST"])
def save_draft_proposal(request):
    if request.method == "POST":
        try:
            proposal_id = request.data.get('proposal_id')
            
            proposal_object = ContractProposal.objects.get(id = proposal_id, user = request.user)
            proposal_object.draft = True
            proposal_object.save()
            print(proposal_id, "-------------------")

            return Response({'messages': "Draft saved successfully"}, status=status.HTTP_200_OK)
        
        except ContractProposal.DoesNotExist:
            return Response({'messages': 'Proposal does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
def delete_draft_proposal(request, proposal_id):
    if request.method == "DELETE":
        try:
            
            proposal_object = ContractProposal.objects.get(id=proposal_id, user=request.user)
            proposal_object.delete()

            return Response({'messages': "Draft deleted successfully"}, status=status.HTTP_200_OK)
        
        except ContractProposal.DoesNotExist:
            return Response({'messages': 'Proposal does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(["GET"])
def draf_proposal_list(request):
    if request.method == "GET":
        try:
            proposal_objects = ContractProposal.objects.filter(user = request.user, draft = True)
            serializers = ContractProposalSerializers(proposal_objects, many = True)
            print(serializers.data, "-------------------")
            
            return Response(serializers.data, status=status.HTTP_200_OK)
           
        
        except ContractProposal.DoesNotExist:
            return Response({'messages': 'Proposal does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
def get_proposal_by_id(request, proposal_id):
    if request.method == "GET":
        try:
            proposal_object = ContractProposal.objects.get(id = proposal_id, user = request.user)
            proposal_object.save()

            return Response({'proposal': proposal_object.proposal}, status=status.HTTP_200_OK)
        
        except ContractProposal.DoesNotExist:
            return Response({'messages': 'Proposal does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['PUT'])
def update_proposal_by_id(request):
    if request.method == "PUT":
        try:
            proposal_id = request.data.get('proposal_id')
            proposal = request.data.get('update_proposal')

            proposal_object = ContractProposal.objects.get(id=proposal_id, user=request.user)
            proposal_object.proposal = proposal
            proposal_object.save()
            print(proposal_object.proposal, "-------------------")
            return Response({"update_proposal": proposal_object.proposal, 'messages': "Proposal updated successfully"}, status=status.HTTP_200_OK)
        
        except ContractProposal.DoesNotExist:
            return Response({'messages': 'Proposal does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def submit_proposal_list(request):
    if request.method == "GET":
        try:
            proposal_objects = ContractProposal.objects.filter(user=request.user, submit=True)
            
            serializers = ContractProposalSerializers(proposal_objects, many=True) 
            return Response(serializers.data, status=status.HTTP_200_OK)
        
        except ContractProposal.DoesNotExist:
            return Response({'messages': "Proposal does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




from io import BytesIO
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from django.core.mail import EmailMessage

def generate_and_save_pdf(text, proposal_id, filename=None):
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)

    width, height = letter
    margin = inch
    x = margin
    y = height - margin

    default_font = "Helvetica"
    bold_font = "Helvetica-Bold"
    font_size = 11

    max_width = width - 2 * margin

    def draw_line_with_bold_tags(line, x, y):
        text_obj = c.beginText(x, y)
        text_obj.setFont(default_font, font_size)

        parts = line.split("**")
        bold = False

        for part in parts:
            if bold:
                text_obj.setFont(bold_font, font_size)
            else:
                text_obj.setFont(default_font, font_size)
            text_obj.textOut(part)
            bold = not bold

        c.drawText(text_obj)

    for line in text.splitlines():
        stripped_line = line.strip()

        # Heading (## Title)
        if stripped_line.startswith("##"):
            heading = stripped_line.lstrip("#").strip()
            c.setFont(bold_font, 14)
            c.drawString(x, y, heading)
            y -= 20

        else:
            # Word wrap manually
            words = stripped_line.split()
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                line_width = stringWidth(test_line, default_font, font_size)
                if line_width <= max_width:
                    current_line = test_line
                else:
                    draw_line_with_bold_tags(current_line, x, y)
                    y -= 14
                    current_line = word
                    if y < margin:
                        c.showPage()
                        y = height - margin

            if current_line:
                draw_line_with_bold_tags(current_line, x, y)
                y -= 14

        if y < margin:
            c.showPage()
            y = height - margin

    c.save()
    pdf_buffer.seek(0)

    contract_proposal = ContractProposal.objects.get(id=proposal_id)
    if filename is None:
        filename = f"proposal_{proposal_id}.pdf"

    contract_proposal.pdf_file.save(filename, ContentFile(pdf_buffer.read()))
    return contract_proposal.pdf_file.url




@api_view(['POST'])
def proposal_pdf(request):
    proposal_id = request.data.get('proposal_id')
    try:        
        if not proposal_id:
            return Response({'message': 'Proposal ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        contract_proposal = ContractProposal.objects.get(id=proposal_id)
        proposal_text = contract_proposal.proposal  
        
        if contract_proposal.pdf_file:
            pdf_url = settings.BASE_URL + contract_proposal.pdf_file.url
            return Response({'pdf': pdf_url}, status=status.HTTP_200_OK)
    
        pdf_url = generate_and_save_pdf(text=proposal_text, proposal_id=proposal_id)
        pdf_url = settings.BASE_URL + pdf_url
        
        return Response({'pdf': pdf_url}, status=status.HTTP_200_OK)

    except ContractProposal.DoesNotExist:
        return Response({'message': 'Proposal does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# @api_view(['POST'])
# @permission_classes([])   
# def download_pdf(request):
#     if request.method == "POST":
#         proposal_id = request.data.get('proposal_id')

#         if not proposal_id:
#             return Response({'error': 'Proposal ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             contract_proposal = ContractProposal.objects.get(id=proposal_id)
#         except ContractProposal.DoesNotExist:
#             return Response({'error': 'Proposal not found.'}, status=status.HTTP_404_NOT_FOUND)

#         proposal_text = contract_proposal.proposal
#         if not proposal_text:
#             return Response({'error': 'Proposal text is empty.'}, status=status.HTTP_400_BAD_REQUEST)

#         pdf_path = generate_pdf(text=proposal_text)

#         contract_proposal.pdf_path = pdf_path
#         contract_proposal.save()

#         return Response({'message': 'PDF generated successfully.', 'pdf_path': pdf_path}, status=status.HTTP_200_OK)



# @api_view(['POST'])
# @permission_classes([])  
# def send_pdf_email_link(request):
#     if request.method == "POST":
#         proposal_id = request.data.get('proposal_id')
#         recipient_email = request.data.get('email')

#         if not proposal_id or not recipient_email:
#             return Response({'error': 'Proposal ID and recipient email are required.'}, status=400)
        
#         try:
#             contract_proposal = ContractProposal.objects.get(id=proposal_id)
#         except ContractProposal.DoesNotExist:
#             return Response({'error': 'Proposal not found.'}, status=404)

#         proposal_text = contract_proposal.proposal
#         if not proposal_text:
#             return Response({'error': 'Proposal text is empty.'}, status=400)

#         pdf_url = generate_and_save_pdf(text=proposal_text, proposal_id=proposal_id)

#         subject = f"Proposal: {contract_proposal.title}"
#         message = f"Please find the proposal attached. You can download the PDF from the following link:\n\n{settings.BASE_URL + pdf_url}"
#         email_from = settings.EMAIL_HOST_USER

#         try:
#             email_message = EmailMessage(
#                 subject=subject,
#                 body=message,
#                 from_email=email_from,
#                 to=[recipient_email],
#             )
#             email_message.send()

#             return Response({'message': 'Email sent successfully with the PDF link.'}, status=200)
        
#         except Exception as e:
#             return Response({'error': f'Error sending email: {str(e)}'}, status=500)

