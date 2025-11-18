from azure.communication.email import EmailClient
from django.conf import settings

def send_acs_email(to_email, subject, html_content, plain_text=""):
    client = EmailClient.from_connection_string(settings.ACS_CONNECTION_STRING)

    message = {
        "senderAddress": settings.ACS_SENDER,
        "recipients": {
            "to": [{"address": to_email}]
        },
        "content": {
            "subject": subject,
            "plainText": plain_text or "Please view this email in HTML mode.",
            "html": html_content,
        }
    }

    poller = client.begin_send(message)
    result = poller.result()
    return result
