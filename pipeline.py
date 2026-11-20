import datetime
import db, ingest, dedup, tag

def run():
    db.init()
    rows = dedup.dedup(ingest.fetch_all())
    now = datetime.datetime.utcnow().isoformat()
    total = len(rows)
    for i, r in enumerate(rows,1):
        try:
            role, city = tag.classify(r)
        except Exception:
            role, city = "Other", "unknown"
        r["role_tag"], r["city_tag"] = role, city
        r["raw_text"] = f"{r['title']} | {r['company']} | {r['location_raw']}"
        r["tagged_at"] = now
        db.upsert(r)
        if i % 10 == 0 or i == total:
            print(f"  tagged {i}/{total}")
    print(f"pipeline done. total rows in db: {db.count()}")


if __name__ == "__main__":
    run()