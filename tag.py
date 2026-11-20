import os, json, requests, datetime

ROLES = ["Software/SDE", "Data/ML/AI", "Frontend", "Backend", "Full Stack",
         "DevOps/Cloud", "QA/Testing", "Product", "Design",
         "Core Engineering (Mech/Civil/Electrical)", "Sales/Marketing",
         "HR/Recruiting", "Finance/Accounting", "Operations",
         "Content/Media", "Healthcare", "Other"]

PROMPT = """You are a strict classifier. You are given one job post. Do two things:
1) role: choose EXACTLY ONE from this list: {roles}
2) city: the Indian city in the post. If no city is clearly stated, return "unknown".
Rules: Do NOT invent or guess. Only use what is in the text. Output ONLY JSON:
{{"role": "<one of the list>", "city": "<city or unknown>"}}

JOB POST:
Title: {title}
Company: {company}
Location: {location}
"""

GEMINI_URL = ("https://generativelanguage.googleapis.com/v1beta/models/"
              "gemini-3.8-flash:generateContent?key={key}")

def classify(job):
    key = os.environ["GEMINI_API_KEY"]
    prompt = PROMPT.format(roles=", ".join(ROLES), title=job["title"],
                           company=job["company"], location=job["location_raw"])
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0, "responseMimeType": "application/json"}}
    r = requests.post(GEMINI_URL.format(key=key), json=body, timeout=20).json()
    if "candidates" not in r:
        raise RuntimeError(str(r)[:200])
    txt = r["candidates"][0]["content"]["parts"][0]["text"]
    out = json.loads(txt)
    role = out.get("role", "Other")
    if role not in ROLES:
        role = "Other"
    city = (out.get("city") or "unknown").strip() or "unknown"
    return role, city

def tag_rows(rows):
    now = datetime.datetime.utcnow().isoformat()
    for r in rows:
        try:
            role, city = classify(r)
        except Exception:
            role, city = "Other", "unknown"
        r["role_tag"], r["city_tag"] = role, city
        r["raw_text"] = f"{r['title']} | {r['company']} | {r['location_raw']}"
        r["tagged_at"] = now
    return rows
