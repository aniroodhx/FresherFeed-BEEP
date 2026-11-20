## Fresher Jobs India
Live tool that collects 300+ fresher and internship posts in India from public
job APIs, dedups them, tags each by role and city using an LLM (classify-only,
never generate), and shows them on a searchable page that refreshes daily on its own.

## Design principle (the important bit)
The LLM is a classifier, not a generator. It picks a role from a fixed list and
extracts the city from the real post text. If the city is not stated it returns
“unknown”, it never guesses. Every tag keeps its raw text and source URL so accuracy
is auditable. This is a direct lesson from a prior project where letting the model
infer missing data caused hallucinated output.

## Sources and terms
Only public job APIs meant for public consumption (Adzuna India, plus Greenhouse and
Lever company boards). No scraping of sites that forbid it. Edit SOURCES in ingest.py
to add boards, and check each board’s terms first.

## Run locally
pip install -r requirements.txt
export ADZUNA_APP_ID=... ADZUNA_APP_KEY=...
export GEMINI_API_KEY=...
python pipeline.py        # ingest, dedup, tag -> jobs.db
uvicorn app:app --reload  # http://127.0.0.1:8000
Daily refresh
.github/workflows/refresh.yml runs pipeline.py every day (07:00 IST) via GitHub Actions
and commits the updated jobs.db. Add the API keys as repo secrets.

## Accuracy and cost
python eval.py export   # writes labels.csv (50 posts), hand-fill true_role/true_city
python eval.py score    # prints role and city accuracy
python eval.py cost     # prints cost per 1,000 posts

## Files
ingest.py fetches from public APIs and filters India plus fresher. dedup.py removes exact
and near-duplicates. tag.py does classify-only LLM tagging (strict JSON, null if absent).
pipeline.py orchestrates them into jobs.db. app.py plus templates/index.html serve the
searchable page and JSON API. eval.py reports accuracy and cost. db.py is the SQLite layer.