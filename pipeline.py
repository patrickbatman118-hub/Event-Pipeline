import random
import pandas as pd
from datetime import datetime, date

from database import get_engine, init_db
from gmail_client import (
    get_gmail_service, fetch_unprocessed_emails,
    get_email_data, fetch_attachment_bytes,
    mark_as_processed, get_label_id
)
from extractor import extract_hero_image_from_html, extract_links, strip_html
from cloudinary_client import upload_image_bytes, upload_image_from_url
from gemini_client import parse_with_gemini


COLOR_OPTIONS = [
    "text-orange-500", "text-blue-500", "text-green-500",
    "text-purple-500", "text-pink-500", "text-red-500"
]


def process_emails():
    init_db()
    engine = get_engine()
    service = get_gmail_service()
    processed_label_id = get_label_id(service, "processed")

    messages = fetch_unprocessed_emails(service)

    for msg_ref in messages:
        message_id = msg_ref["id"]
        try:
            _process_single_email(service, engine, message_id, processed_label_id)
        except Exception as e:
            print(f"Failed on message {message_id}: {e}")
            continue


def _process_single_email(service, engine, message_id, processed_label_id):
    email = get_email_data(service, message_id)
    html = email["html"]

    image_url = ""

    # Try attachment first
    if email["attachments"]:
        largest = max(email["attachments"], key=lambda a: a["size"])
        try:
            image_bytes = fetch_attachment_bytes(service, message_id, largest["attachment_id"])
            image_url = upload_image_bytes(
                image_bytes,
                largest["mime_type"],
                f"event_{message_id}"
            )
        except Exception as e:
            print(f"Attachment upload failed: {e}")

    # Fallback to HTML hero image
    if not image_url and html:
        hero_url = extract_hero_image_from_html(html)
        if hero_url and hero_url.startswith("http"):
            try:
                image_url = upload_image_from_url(hero_url, f"event_{message_id}")
            except Exception as e:
                print(f"URL upload failed: {e}")

    clean_text = strip_html(html)[:2000]
    links = extract_links(html)

    event = parse_with_gemini(clean_text + "\nImportant Links:\n" + "\n".join(links))

    if not event.get("registerLink") or len(event["registerLink"]) < 10:
        event["registerText"] = ""
        event["registerLink"] = ""

    row = {
        "tag": "NEW",
        "title": event.get("title", ""),
        "description": event.get("description", ""),
        "image": image_url,
        "tag_color": random.choice(COLOR_OPTIONS),
        "bg_color": "#ffffff",
        "date": event.get("date") or None,
        "start_time": event.get("startTime", ""),
        "end_time": event.get("endTime", ""),
        "venue": event.get("venue", ""),
        "event_link": event.get("eventLink", ""),
        "text_color": "#ffffff",
        "title_color": "#ffffff",
        "info": event.get("info", ""),
        "register_text": event.get("registerText", ""),
        "register_link": event.get("registerLink", ""),
        "message_id": message_id,
        "uploaded_at": datetime.utcnow()
    }

    df = pd.DataFrame([row])
    df.to_sql("events", con=engine, if_exists="append", index=False)

    mark_as_processed(service, message_id, processed_label_id)
    print(f"Processed: {event.get('title', message_id)}")


def remove_expired_events():
    engine = get_engine()
    today = date.today()

    with engine.connect() as conn:
        from sqlalchemy import text
        conn.execute(text("""
            DELETE FROM events
            WHERE date IS NOT NULL
            AND date < :today
        """), {"today": today})
        conn.commit()


def remove_new_tags():
    engine = get_engine()
    with engine.connect() as conn:
        from sqlalchemy import text
        conn.execute(text("""
            UPDATE events
            SET tag = '', tag_color = ''
            WHERE tag = 'NEW'
            AND uploaded_at < DATEADD(hour, -24, GETDATE())
        """))
        conn.commit()


if __name__ == "__main__":
    process_emails()
