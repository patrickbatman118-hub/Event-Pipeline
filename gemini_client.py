import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"


def parse_with_gemini(text):
    prompt = f"""
Return ONLY JSON:

{{
  "title": "",
  "description": "",
  "date": "",
  "startTime": "",
  "endTime": "",
  "venue": "",
  "eventLink": "",
  "info": "",
  "registerText": "",
  "registerLink": ""
}}

Rules:
- title: Max 3-4 words. It MUST include the specific subject/brand of the event so it makes sense in a standalone calendar. Format as [Subject] [Event Type]. 
- description: Write a single, punchy phrase (maximum 8 words) that acts as a subtitle on a UI card. Focus strictly on the value or action. No fluff, no periods at the end.
- info: Write a hyper-concise, 2-3 sentence news brief. 
  - GOAL: Save the student's time. Deliver only the core facts.
  - FATAL ERROR if you use marketing fluff, dramatic adjectives, or filler words.
  - Maintain a premium, objective reporting tone.
  - Do NOT use bullet points or line breaks.
- pick main event date
- format the date strictly as YYYY-MM-DD
- detect time, venue
- choose best link as registerLink
- ignore useless links
- ignore link : https://discourse.iitm.ac.in/
- if no link → registerLink = ""

Email:
{text}
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(
        GEMINI_URL,
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()

    data = response.json()
    if "candidates" not in data:
        raise ValueError("Gemini error: " + response.text)

    output = data["candidates"][0]["content"]["parts"][0]["text"]
    output = output.replace("```json", "").replace("```", "").strip()

    return json.loads(output)
