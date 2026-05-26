# Event Pipeline

Fetches emails from Gmail, extracts event data using Gemini AI, uploads images to Cloudinary, and stores structured records in MS SQL Server.

## Setup

**1. Install dependencies**
```
pip install -r requirements.txt
```

**2. Gmail API credentials**
- Go to Google Cloud Console
- Enable Gmail API
- Download `credentials.json` and place it in this folder
- First run will open a browser for auth and generate `token.json`

**3. Environment variables**
```
cp .env.example .env
```
Fill in your keys in `.env`

**4. Gmail labels**
Make sure you have two labels in Gmail:
- `events` — emails you want processed
- `processed` — pipeline marks emails here after processing

**5. Initialize DB and run**
```
python pipeline.py
```

## Files

| File | What it does |
|---|---|
| pipeline.py | Main orchestrator, run this |
| gmail_client.py | Gmail API auth and email fetching |
| extractor.py | HTML parsing, image scoring, link extraction |
| cloudinary_client.py | Image uploads |
| gemini_client.py | LLM parsing |
| database.py | DB connection and table creation |

## Scheduled runs

Use Windows Task Scheduler or cron to run `pipeline.py` on an interval.

Example cron (every 30 mins):
```
*/30 * * * * /usr/bin/python3 /path/to/pipeline.py
```
