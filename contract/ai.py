import google.generativeai as genai
from datetime import datetime

api_key = "AIzaSyB01ouUyKFz7IGzCgEnBdHnEY9QRQXPfIQ"  
genai.configure(api_key=api_key)
    
# {
#         "noticeId": "fcfd50c27639416bb40825e8a410da8c",
#         "title": "30--WEIGHT,COUNTERBALAN",
#         "solicitationNumber": "SPE7M125T8227",
#         "fullParentPathName": "DEPT OF DEFENSE.DEFENSE LOGISTICS AGENCY.DLA MARITIME.DLA MARITIME COLUMBUS.DLA LAND AND MARITIME",
#         "fullParentPathCode": "097.97AS.DLA MARITIME.DLA MARITIME COLUMBS.SPE7M1",
#         "postedDate": "2025-03-16",
#         "type": "Combined Synopsis/Solicitation",
#         "baseType": "Combined Synopsis/Solicitation",
#         "archiveType": "autocustom",
#         "archiveDate": "2025-04-26",
#         "typeOfSetAsideDescription": "Total Small Business Set-Aside (FAR 19.5)",
#         "typeOfSetAside": "SBA",
#         "responseDeadLine": "2025-03-27",
#         "naicsCode": "333613",
#         "naicsCodes": [
#             "333613"
#         ],
#         "classificationCode": "30",
#         "active": "Yes",
#         "award": null,
#         "pointOfContact": [
#             {
#                 "fax": null,
#                 "type": "primary",
#                 "email": "DibbsBSM@dla.mil",
#                 "phone": null,
#                 "title": null,
#                 "fullName": "Questions regarding this solicitation should be emailed to the buyer listed in block 5 of the solicitation document which can be found under the Additional Information link.\nIf the Additional Information link does not work, please go to https://www.dibbs.bsm.dla.mil/Solicitations/ and type the solicitation number in the Global Search box.\n"
#             }
#         ],
#         "description": "https://api.sam.gov/prod/opportunities/v1/noticedesc?noticeid=fcfd50c27639416bb40825e8a410da8c",
#         "organizationType": "OFFICE",
#         "officeAddress": {
#             "zipcode": "43218-3990",
#             "city": "COLUMBUS",
#             "countryCode": "USA",
#             "state": "OH"
#         },
#         "placeOfPerformance": null,
#         "additionalInfoLink": null,
#         "uiLink": "https://sam.gov/opp/fcfd50c27639416bb40825e8a410da8c/view",
#         "links": [
#             {
#                 "rel": "self",
#                 "href": "https://api.sam.gov/prod/opportunities/v2/search?noticeid=fcfd50c27639416bb40825e8a410da8c&limit=1"
#             }
#         ],
#         "resourceLinks": null
#     }

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

    
    Point Of Contact:
    - Fax: {notice_details['pointOfContact'][0]['fax']}
    - Type: {notice_details['pointOfContact'][0]['type']}
    - Email: {notice_details['pointOfContact'][0]['email']}
    - phone: {notice_details['pointOfContact'][0]['phone']}
    - Title: {notice_details['pointOfContact'][0]['title']}
    - Full Name: {notice_details['pointOfContact'][0]['fullName']}
    

    office Address:
    - Office Zipcode: {notice_details['officeAddress']['zipcode']}
    - Office City: {notice_details['officeAddress']['city']}
    - Office Country Code: {notice_details['officeAddress']['countryCode']}
    - Office State: {notice_details['officeAddress']['state']}
    

    The cover letter should include a professional introduction, statement of interest, and relevant qualifications.
    The contract proposal should clearly outline the scope of services, terms, pricing, and duration of the contract.

    Note: The output should be formatted in Markdown so that it can be properly displayed in the frontend. Don't make any table in the output.
    """
    
    response = genai.GenerativeModel("gemini-1.5-flash").generate_content([prompt])
    return response.text  



# cover_letter_and_proposal = generate_cover_letter_and_proposal(description_, notice_details_)
# print(cover_letter_and_proposal)




genai.configure(api_key=api_key)

def generate_recommendations_for_cover_letter_and_contract(project_description: str):
    prompt = f"""
    Given the following project description, provide a **requirement analysis** and **concise recommendations** for the key elements to include in a cover letter and contract proposal.

    Project Description:
    {project_description}

    **Requirement Analysis**:
    Identify the specific needs and requirements of the project from the description, including any important conditions or constraints.

    **Recommendations for the Cover Letter**:
    1. What to include in the introduction.
    2. Relevant experience to highlight.
    3. How to demonstrate the ability to meet the project's requirements.
    4. Suggestions for expressing interest and fit for the project.

    **Recommendations for the Contract Proposal**:
    1. Key points to include in the project scope and deliverables.
    2. Suggestions for outlining timelines, performance periods, and milestones.
    3. Payment terms and budget recommendations.
    4. Qualifications and experience to emphasize.
    5. Compliance requirements (legal, regulatory, accessibility).
    6. Key evaluation criteria to consider for the provider selection.
    """
    
    response = genai.GenerativeModel("gemini-1.5-flash").generate_content([prompt])
    return response.text.strip()

description = """
The Federal Bureau of Prisons, CTS Contracting Office, Washington, D.C. is seeking quotes from sources
that have the ability to provide community-based outpatient substance use disorder, mental health, and sex offender
treatment services for male and female Adults in Custody (AICs) residing at the local Residential Reentry Center (RRC),
and/or on home confinement, or on Federal Location Monitoring (FLM), or, if applicable, reporting to a Day Reporting Center,
in the Memphis, TN area. All treatment services will be required to be performed within a 10-mile radius of Memphis City Hall
located at 125 N Main Street, Memphis, TN 38103, within a 1/2-mile access to community-based transportation, and within the state of Tennessee.
Performance periods under this contract will be for a one-year base period estimated to begin on October 01, 2024, with four (4) one-year option periods,
with services ending (if all options years are renewed) on September 30, 2029. These services required for this contract include a Base Year;
Option Year One, Option Year Two, Option Year Three, and Option Year Four.
"""

# recommendations = generate_recommendations_for_cover_letter_and_contract(description)
# print(recommendations)