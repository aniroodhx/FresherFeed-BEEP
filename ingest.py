"""Collect fresher/intern job posts in India from PUBLIC job APIs.

Primary source: Adzuna India API (official, free key, ToS-clean) -> bulk volume.
Bonus sources: Greenhouse & Lever public company boards.
No scraping of sites that forbid it.
"""
import os, requests, datetime

# --- Bonus: company boards (optional). provider: "greenhouse"|"lever", token=slug ---
SOURCES = [
    ("greenhouse", "razorpaysoftwareprivatelimited"),
    # add more real slugs here if you want; Adzuna below is the main volume source
]

FRESHER_HINTS = ("intern", "fresher", "graduate", "entry", "trainee", "junior",
                 "0-1", "0-2", "new grad", "associate", "campus")
INDIA_HINTS   = ("india", "bengaluru", "bangalore", "mumbai", "pune", "chennai",
                 "hyderabad", "delhi", "gurgaon", "gurugram", "noida", "kolkata")

def _is_india(loc):    return any(h in (loc or "").lower() for h in INDIA_HINTS)
def _is_fresher(title):return any(h in (title or "").lower() for h in FRESHER_HINTS)

# ---------------- Adzuna India (primary) ----------------
def _adzuna(pages=8, per_page=50):
    app_id  = os.environ["ADZUNA_APP_ID"]
    app_key = os.environ["ADZUNA_APP_KEY"]
    out = []
    for page in range(1, pages + 1):
        u = (f"https://api.adzuna.com/v1/api/jobs/in/search/{page}"
             f"?app_id={app_id}&app_key={app_key}&results_per_page={per_page}"
             f"&what_or=intern graduate trainee fresher entry level junior associate&max_days_old=30")
        data = requests.get(u, timeout=25).json()
        for j in data.get("results", []):
            out.append({
                "title": j.get("title", ""),
                "company": (j.get("company") or {}).get("display_name", ""),
                "location_raw": (j.get("location") or {}).get("display_name", ""),
                "url": j.get("redirect_url", ""),
                "source": "adzuna:in",
            })
    return out

# ---------------- Company boards (bonus) ----------------
def _greenhouse(token):
    u = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    data = requests.get(u, timeout=20).json()
    return [{
        "title": j.get("title",""), "company": token,
        "location_raw": (j.get("location") or {}).get("name",""),
        "url": j.get("absolute_url",""), "source": f"greenhouse:{token}",
    } for j in data.get("jobs", [])]

def _lever(token):
    u = f"https://api.lever.co/v0/postings/{token}?mode=json"
    data = requests.get(u, timeout=20).json()
    if not isinstance(data, list):   # invalid slug -> error object, skip safely
        raise ValueError("unexpected Lever response (bad slug?)")
    return [{
        "title": j.get("text",""), "company": token,
        "location_raw": (j.get("categories") or {}).get("location",""),
        "url": j.get("hostedUrl",""), "source": f"lever:{token}",
    } for j in data]

def fetch_all():
    rows, now = [], datetime.datetime.utcnow().isoformat()

    # primary bulk source
    try:
        got = _adzuna()
        print(f"  adzuna:in -> {len(got)} posts")
        rows += got
    except Exception as e:
        print(f"  !! adzuna failed: {e}")

    # bonus boards
    for provider, token in SOURCES:
        try:
            got = _greenhouse(token) if provider == "greenhouse" else _lever(token)
            print(f"  {provider}:{token} -> {len(got)} posts")
            rows += got
        except Exception as e:
            print(f"  !! {provider}:{token} failed: {e}")

    kept = []
    for r in rows:
        if _is_india(r["location_raw"]) and _is_fresher(r["title"]):
            r["fetched_at"] = now
            kept.append(r)
    print(f"kept {len(kept)} India fresher posts (of {len(rows)} fetched)")
    return kept

if __name__ == "__main__":
    for r in fetch_all()[:5]:
        print(r["title"], "|", r["company"], "|", r["location_raw"])
