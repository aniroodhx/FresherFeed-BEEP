"""Accuracy + cost report — the 'put a number on it' deliverable.

1) Export 50 posts to labels.csv, hand-fill true_role/true_city columns.
2) Run this: it compares your labels to the LLM tags and prints accuracy + cost.
"""
import csv, sys, db

# Gemini 2.0 Flash approx pricing (USD per 1M tokens) — UPDATE to current rates.
IN_PER_M, OUT_PER_M = 0.10, 0.40
AVG_IN_TOK, AVG_OUT_TOK = 120, 20   # measure real averages and replace these

def export_template(n=50):
    rows = db.all_jobs()[:n]
    with open("labels.csv","w",newline="") as f:
        w = csv.writer(f)
        w.writerow(["id","title","company","location_raw","llm_role","llm_city","true_role","true_city"])
        for r in rows:
            w.writerow([r["id"],r["title"],r["company"],r["location_raw"],
                        r["role_tag"],r["city_tag"],"",""])
    print(f"wrote labels.csv with {len(rows)} rows — hand-fill true_role/true_city")

def score():
    role_ok=city_ok=n=0
    with open("labels.csv") as f:
        for r in csv.DictReader(f):
            if not r["true_role"].strip(): continue
            n+=1
            role_ok += r["llm_role"].strip().lower()==r["true_role"].strip().lower()
            city_ok += r["llm_city"].strip().lower()==r["true_city"].strip().lower()
    print(f"labeled: {n}")
    print(f"role accuracy: {role_ok}/{n} = {role_ok/n*100:.1f}%")
    print(f"city accuracy: {city_ok}/{n} = {city_ok/n*100:.1f}%")

def cost():
    per_post = (AVG_IN_TOK/1e6*IN_PER_M) + (AVG_OUT_TOK/1e6*OUT_PER_M)
    print(f"~${per_post*1000:.3f} per 1,000 posts "
          f"(in {AVG_IN_TOK} tok, out {AVG_OUT_TOK} tok/post)")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv)>1 else "cost"
    {"export":export_template, "score":score, "cost":cost}[cmd]()
