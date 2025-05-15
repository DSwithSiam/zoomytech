import sib_api_v3_sdk
from django.template.loader import render_to_string
from sib_api_v3_sdk.rest import ApiException

API_KEY = "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"


def send_email(user_email, email_subject, email_body):
    print("Sending email to: ====== ", user_email)

    # Set up API key and client configuration
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # Prepare the email content
    email_subject = email_subject
    email_body = email_body

    sender = {"name": "Zoomytech", "email": "info@birdboxtools.com"}
    recipient = [{"email": user_email, "name": "User"}]

    email_content = sib_api_v3_sdk.SendSmtpEmail(
        sender=sender,
        to=recipient,
        subject=email_subject,
        html_content=email_body
    )

    
    try:
        api_instance.send_transac_email(email_content)
        print("Email sent successfully!")
    except ApiException as e:
        print("Error sending email:", e)