import google.generativeai as genai
from datetime import datetime

api_key = "AIzaSyB01ouUyKFz7IGzCgEnBdHnEY9QRQXPfIQ"  
genai.configure(api_key=api_key)
    
# notice_details_ = {
#     'noticeId': 'fcaf4a7bdb5c4550b374b7aa66089a2b',
#     'title': 'SU/MH/SOT in Memphis, TN',
#     'solicitationNumber': '15BCTS24Q00000007',
#     'fullParentPathName': 'JUSTICE, DEPARTMENT OF.FEDERAL PRISON SYSTEM / BUREAU OF PRISONS.COMMUNITY TREATMENT SERVICES - CO',
#     'postedDate': '2024-04-05',
#     'type': 'Presolicitation',
#     'typeOfSetAsideDescription': 'Total Small Business Set-Aside (FAR 19.5)',
#     'responseDeadLine': '2024-04-19T12:00:00-04:00',
#     'naicsCode': '621420',
#     'classificationCode': 'G004',
#     'pointOfContact': [
#         {
#             'email': 'k1warner@bop.gov',
#             'phone': '2025986139',
#             'fullName': 'Kia Warner'
#         },
#         {
#             'email': 'r1carroll@bop.gov',
#             'phone': '2025986124',
#             'fullName': 'Robert Carroll'
#         }
#     ],
#     'companyDetails': {
#         'companyName': 'XYZ Healthcare Solutions',
#         'address': '123 Business Ave, Suite 400, Memphis, TN 38001',
#         'phone': '+1 800-555-0101',
#         'email': 'contact@xyzhealthcare.com',
#     }
# }

# description_ = """
# The Federal Bureau of Prisons, CTS Contracting Office, Washington, D.C. is seeking quotes from sources
# that have the ability to provide community-based outpatient substance use disorder, mental health, and sex offender
# treatment services for male and female Adults in Custody (AICs) residing at the local Residential Reentry Center (RRC),
# and/or on home confinement, or on Federal Location Monitoring (FLM), or, if applicable, reporting to a Day Reporting Center,
# in the Memphis, TN area. All treatment services will be required to be performed within a 10-mile radius of Memphis City Hall
# located at 125 N Main Street, Memphis, TN 38103, within a 1/2-mile access to community-based transportation, and within the state of Tennessee.
# Performance periods under this contract will be for a one-year base period estimated to begin on October 01, 2024, with four (4) one-year option periods,
# with services ending (if all options years are renewed) on September 30, 2029. These services required for this contract include a Base Year;
# Option Year One, Option Year Two, Option Year Three, and Option Year Four.
# """


todays_date = datetime.now().strftime("%B %d, %Y")  

def generate_cover_letter_and_proposal(description, notice_details):
    prompt = f"""
    Based on the description below, write a formal cover letter and contract proposal.

    Description:
    {description}

    Contract Notice Details:
    - Notice ID: {notice_details['noticeId']}
    - Title: {notice_details['title']}
    - Solicitation Number: {notice_details['solicitationNumber']}
    - Posted Date: {notice_details['postedDate']}
    - Type: {notice_details['type']}
    - Set-Aside: {notice_details['typeOfSetAsideDescription']}
    - NAICS Code: {notice_details['naicsCode']}
    - Classification Code: {notice_details['classificationCode']}
    - Response Deadline: {notice_details['responseDeadLine']}
    
    Company Information:
    - Company Name: {notice_details['companyDetails']['companyName']}
    - Company Address: {notice_details['companyDetails']['address']}
    - Contact Email: {notice_details['companyDetails']['email']}
    - Contact Phone: {notice_details['companyDetails']['phone']}
    
    The cover letter should include a professional introduction, statement of interest, and relevant qualifications.
    The contract proposal should clearly outline the scope of services, terms, pricing, and duration of the contract.

    Note: The output should be formatted in Markdown so that it can be properly displayed in the frontend. Don't make any table in the output.
    """
    
    response = genai.GenerativeModel("gemini-1.5-flash").generate_content([prompt])
    return response.text  



# cover_letter_and_proposal = generate_cover_letter_and_proposal(description_, notice_details_)
# print(cover_letter_and_proposal)