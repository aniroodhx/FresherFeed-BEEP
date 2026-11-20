"""Dedup: exact (normalized hash) + near-duplicate (same company + similar title)."""
import hashlib, re
from difflib import SequenceMatcher

def _norm(s): return re.sub(r"\s+", " ", (s or "").strip().lower())

def key(job):
    base = f"{_norm(job['title'])}|{_norm(job['company'])}|{_norm(job['location_raw'])}"
    return hashlib.sha1(base.encode()).hexdigest()

def titles_similar(a, b, threshold):
    return SequenceMatcher(None, _norm(a), _norm(b)).ratio() >= threshold

def dedup(rows, title_threshold=0.92):
    seen_hash = set()
    kept = []
    for r in rows:
        r = dict(r)
        r["id"] = key(r)

        # 1. exact duplicate (same normalized title+company+location)
        if r["id"] in seen_hash:
            continue

        # 2. near-duplicate: same company + very similar title already kept
        is_near_dup = False
        for k in kept:
            if r["company"] == k["company"] and titles_similar(r["title"], k["title"], title_threshold):
                is_near_dup = True
                break
        if is_near_dup:
            continue

        seen_hash.add(r["id"])
        kept.append(r)

    print(f"dedup: {len(rows)} -> {len(kept)}")
    return kept

if __name__ == "__main__":
    demo = [{"title":"SDE Intern","company":"x","location_raw":"Pune"},
            {"title":"SDE  Intern","company":"x","location_raw":"Pune"}]
    print(len(dedup(demo)))
