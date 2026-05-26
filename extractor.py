import re
from bs4 import BeautifulSoup


def extract_hero_image_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    imgs = soup.find_all("img")

    best_url = ""
    best_score = 0

    blocklist = ["logo", "icon", "avatar", "spacer", "banner", "footer", "signature"]

    for img in imgs:
        src = img.get("src", "")
        if not src or not src.startswith("http"):
            continue

        lower = src.lower()
        if any(word in lower for word in blocklist):
            continue
        if lower.endswith(".gif"):
            continue

        try:
            width = int(img.get("width", 0))
            height = int(img.get("height", 0))
        except (ValueError, TypeError):
            width = height = 0

        if width > 0 and width < 300:
            continue
        if width > 0 and height > 0 and width > height * 1.8:
            continue

        score = width + height
        if lower.endswith(".jpg") or lower.endswith(".png"):
            score += 100
        if score == 0:
            score = 50

        if score > best_score:
            best_score = score
            best_url = src

    return best_url


def extract_links(html):
    soup = BeautifulSoup(html, "html.parser")
    links = []

    skip = ["instagram", "facebook", "linkedin", "twitter", "unsubscribe", "mailto", "calendar.google.com", ".ics", "outlook.office365.com", "outlook.live.com"]
    keep = ["register", "join", "whatsapp", "apply", "ticket", "event", "form"]

    for a in soup.find_all("a", href=True):
        url = a["href"].lower()
        if any(s in url for s in skip):
            continue
        if any(k in url for k in keep):
            links.append(a["href"])

    return links


def strip_html(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["style", "script"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    return " ".join(text.split()).strip()
