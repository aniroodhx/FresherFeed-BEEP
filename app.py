"""Searchable page + tiny JSON API. FastAPI so it's a few lines and easy to edit live."""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import pathlib, db

app = FastAPI()
templates = Jinja2Templates(directory=str(pathlib.Path(__file__).parent / "templates"))

@app.get("/api/jobs")
def api_jobs(q: str = "", role: str = "", city: str = ""):
    q, role, city = q.lower(), role.lower(), city.lower()
    results = []
    for j in db.all_jobs():
        text = (j["title"] + " " + j["company"]).lower()
        if q and q not in text:
            continue
        if role and role not in (j["role_tag"] or "").lower():
            continue
        if city and city not in (j["city_tag"] or "").lower():
            continue
        results.append(j)
    return JSONResponse(results)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    rows = db.all_jobs()
    roles = sorted({j["role_tag"] for j in rows if j["role_tag"]})
    cities = sorted({j["city_tag"] for j in rows if j["city_tag"] and j["city_tag"] != "unknown"})
    return templates.TemplateResponse(request, "index.html",
        {"count": len(rows), "roles": roles, "cities": cities})
