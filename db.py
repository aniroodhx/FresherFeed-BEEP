"""SQLite layer. One table: jobs. Kept tiny so it's easy to change live."""
import sqlite3, pathlib

DB = pathlib.Path(__file__).parent / "jobs.db"

def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init():
    with conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id           TEXT PRIMARY KEY,   -- dedup hash
            title        TEXT,
            company      TEXT,
            location_raw TEXT,               -- as given by source
            url          TEXT,
            source       TEXT,               -- which API it came from
            raw_text     TEXT,               -- text we fed the LLM (audit trail)
            role_tag     TEXT,               -- LLM output
            city_tag     TEXT,               -- LLM output ('unknown' if absent)
            tagged_at    TEXT,
            fetched_at   TEXT
        )""")

def upsert(job):
    with conn() as c:
        c.execute("""INSERT INTO jobs
            (id,title,company,location_raw,url,source,raw_text,role_tag,city_tag,tagged_at,fetched_at)
            VALUES (:id,:title,:company,:location_raw,:url,:source,:raw_text,:role_tag,:city_tag,:tagged_at,:fetched_at)
            ON CONFLICT(id) DO UPDATE SET
              role_tag=excluded.role_tag, city_tag=excluded.city_tag,
              tagged_at=excluded.tagged_at, fetched_at=excluded.fetched_at""", job)

def all_jobs():
    with conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM jobs ORDER BY fetched_at DESC")]

def count():
    with conn() as c:
        return c.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]

if __name__ == "__main__":
    init(); print("db ready at", DB, "rows:", count())
