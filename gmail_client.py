import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def get_gmail_service():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

def fetch_unprocessed_emails(service):
    events_label_id = get_label_id(service, "events")
    processed_label_id = get_label_id(service, "processed")

    if not events_label_id:
        raise ValueError("Gmail label 'events' not found")

    result = service.users().messages().list(
        userId="me",
        labelIds=[events_label_id],
        q=f"-label:processed"
    ).execute()

    return result.get("messages", [])


def get_email_data(service, message_id):
    msg = service.users().messages().get(
        userId="me",
        id=message_id,
        format="full"
    ).execute()

    payload = msg["payload"]
    headers = {h["name"]: h["value"] for h in payload.get("headers", [])}
    subject = headers.get("Subject", "")

    html_body = ""
    attachments = []

    def parse_parts(parts):
        for part in parts:
            mime = part.get("mimeType", "")
            if mime == "text/html" and not html_body:
                data = part.get("body", {}).get("data", "")
                if data:
                    decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                    attachments.append({"__html": decoded})
            elif mime.startswith("image/"):
                att_id = part.get("body", {}).get("attachmentId")
                size = part.get("body", {}).get("size", 0)
                if att_id and size > 20000:
                    attachments.append({
                        "attachment_id": att_id,
                        "mime_type": mime,
                        "filename": part.get("filename", "image"),
                        "size": size
                    })
            if "parts" in part:
                parse_parts(part["parts"])

    if "parts" in payload:
        parse_parts(payload["parts"])

    # Separate html from attachments
    html = ""
    real_attachments = []
    for item in attachments:
        if "__html" in item:
            html = item["__html"]
        else:
            real_attachments.append(item)

    return {
        "message_id": message_id,
        "subject": subject,
        "html": html,
        "attachments": real_attachments
    }


def fetch_attachment_bytes(service, message_id, attachment_id):
    att = service.users().messages().attachments().get(
        userId="me",
        messageId=message_id,
        id=attachment_id
    ).execute()
    return base64.urlsafe_b64decode(att["data"])


def mark_as_processed(service, message_id, processed_label_id):
    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"addLabelIds": [processed_label_id]}
    ).execute()


def get_label_id(service, label_name):
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    for label in labels:
        if label["name"].lower() == label_name.lower():
            return label["id"]
    return None
