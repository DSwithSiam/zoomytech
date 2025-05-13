from openai import OpenAI
from datetime import datetime

DEEPSEEK_API_KEY = "sk-861a0b079e1149b4bbf3dfb3d63fbfc8"
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def generate_cover_letter_and_proposal(description, notice_details, company_details, budget):

    prompt = f"""
    Generate a professional government contract submission containing:
    1. Formal Cover Letter
    2. Detailed Service Proposal

    **Contract Opportunity Details:**
    {description}

    **Solicitation Information:**
    {notice_details}

    **Company Details (Only the following info is required):**
    - Name: {company_details['name']}
    - Address: {company_details['street']}, {company_details['city']}, {company_details['state']}, {company_details['zipcode']}
    - Email: {company_details['email']}
    - Phone: {company_details['phone']}
    - Website: {company_details['website']}

    **Requirements:**
    - Cover Letter (1 page):
      * Company introduction
      * Statement of qualifications
      * Expression of interest
      * Contact information

    - Technical Proposal (2-3 pages):
      * Understanding of requirements
      * Technical approach/methodology
      * Relevant experience
      * Staffing plan
      * Quality control measures

    - Business Proposal (1-2 pages):
      * Pricing structure: Estimated project cost is ${budget}. Detailed budget breakdown available upon request.
      * Payment terms with real amount in USD
      * Timeline
      * Terms and conditions

    **Formatting:**
    - No tables (use bullet points instead)
    - Professional business tone
    - Clear section headings

    **Important Instructions:**
    - Use only the company details as provided in the `company_details` object above. **Do not include any placeholders like `[Your Name]` or `[Your Title]`**, as those are not required for this submission.
    - Ensure that all information is presented clearly and professionally.
    - Only include the details mentioned in the `company_details` field and omit all other extra information that is not part of the data provided.
    - Don't write headings like 'End of Proposal'.
    """

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a government contracts specialist helping to prepare a competitive proposal submission."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=5000,
        stream=False
    )

    return response.choices[0].message.content







def generate_recommendations_for_cover_letter_and_contract(project_description: str) -> str:
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

    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {"role": "system", "content": "You are an expert in government contracting and procurement documentation."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1500,
        stream=False
    )

    return response.choices[0].message.content.strip()

