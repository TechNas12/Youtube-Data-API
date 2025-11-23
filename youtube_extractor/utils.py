import os, logging, isodate, time, requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("YT_DATA_API")
BASE = "https://www.googleapis.com/youtube/v3"

# ======================================================
# SAFE REQUEST WRAPPER
# ======================================================
def safe_get(url, params, retries=3):
    """Safe GET request with retries."""
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=20)
            if r.status_code == 200:
                return r.json()
            print(f"[WARN] API error {r.status_code}: {r.text}")
        except Exception as e:
            print(f"[ERROR] Request failed: {e}")
    raise Exception("API request failed repeatedly.")

# ======================================================
# PARSE ISO DURATION (PT3M12S -> seconds)
# ======================================================
def parse_iso_duration(duration):
    try:
        import isodate
        td = isodate.parse_duration(duration)
        return int(td.total_seconds())
    except:
        return None