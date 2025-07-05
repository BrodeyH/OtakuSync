import csv
import re
import time
import requests
import json
from datetime import datetime, timedelta
from imdb import IMDb
from concurrent.futures import ThreadPoolExecutor

# === CONFIG ===
input_file = "anime list.csv"
trakt_output = "trakt-import.csv"
json_output = "trakt-import.json"
progress_output = "watch_progress.csv"
missing_output = "missing_ids.csv"
verified_output = "trakt-verified.csv"
unverified_output = "trakt-unverified.csv"
max_threads = 10
TRAKT_CLIENT_ID = "82df7078b6c5b2c14992a75fd601f189966f28c770c90f2cccf5c837984a1bd7"
now = datetime.utcnow().isoformat(timespec="seconds") + "Z"

# === SETUP ===
ia = IMDb()
episodate_search_url = "https://www.episodate.com/api/search?q="
episodate_details_url = "https://www.episodate.com/api/show-details?q="
trakt_search_url = "https://api.trakt.tv/search/imdb/"

# === HELPERS ===
def normalize(title): return re.sub(r"[^\w\s]", "", title.lower()).strip()
def is_favorite(title, notes): return "favorite" in (title + notes).lower()

def parse_episode_info(text):
    patterns = [r"s(?:eason)?\s*(\d+)\s*e(?:pisode)?\s*(\d+)", r"s(\d+)\s*e(\d+)", r"(\d+)[xX](\d+)"]
    for p in patterns:
        m = re.search(p, text or "", re.IGNORECASE)
        if m: s, e = m.groups(); return f"S{int(s):02}E{int(e):02}"
    return ""

def get_latest_episode_episodate(title):
    print(f"🌐 Episodate: {title}")
    try:
        search = requests.get(episodate_search_url + requests.utils.quote(title)).json()
        shows = search.get("tv_shows", [])
        if not shows: return ""
        permalink = shows[0]["permalink"]
        details = requests.get(episodate_details_url + permalink).json()
        eps = details.get("tvShow", {}).get("episodes", [])
        if eps: last = eps[-1]; return f"S{int(last['season']):02}E{int(last['episode']):02}"
    except Exception as e:
        print(f"⚠️ Episodate failed for {title} → {e}")
    return ""

def try_imdb_lookup(title):
    print(f"🔁 IMDb retry: {title}")
    try:
        results = ia.search_movie(title)
        if results: return f"tt{results[0].movieID}"
    except Exception as e:
        print(f"⚠️ IMDb error: {title} → {e}")
    return ""

def verify_trakt_id(imdb_id):
    headers = {
        "trakt-api-version": "2",
        "trakt-api-key": TRAKT_CLIENT_ID,
        "Content-Type": "application/json"
    }
    try:
        r = requests.get(trakt_search_url + imdb_id, headers=headers)
        return r.status_code == 200 and bool(r.json())
    except: return False

# === STATE ===
show_cache = {}
missing_rows = []
retry_rows = []

def enrich_row(row):
    title = row["Title"].strip()
    title_norm = normalize(title)
    lastep = row.get("lastepwatched", "")
    notes = row.get("notes", "")

    print(f"🔍 {title}")
    row["lastepwatched"] = parse_episode_info(lastep) or parse_episode_info(title) or get_latest_episode_episodate(title)

    imdb_id = row.get("imdb_id", "").strip()
    if not imdb_id:
        imdb_id = show_cache.get(title_norm)
        if not imdb_id:
            try:
                results = ia.search_movie(title)
                if results:
                    imdb_id = f"tt{results[0].movieID}"
                    show_cache[title_norm] = imdb_id
                    print(f"✔️ IMDb: {imdb_id}")
            except: imdb_id = ""
    row["imdb_id"] = imdb_id
    if not imdb_id: retry_rows.append(row)
    return row

# === LOAD ===
with open(input_file, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
    for r in rows:
        r.setdefault("lastepwatched", "")
        r.setdefault("notes", "")

# === ENRICH ===
print(f"\n🚀 Enriching {len(rows)} titles...\n")
start = time.time()
results = []

with ThreadPoolExecutor(max_threads) as pool:
    for i, row in enumerate(pool.map(enrich_row, rows), 1):
        elapsed = time.time() - start
        avg = elapsed / i
        eta = timedelta(seconds=int(avg * (len(rows) - i)))
        print(f"📊 {i}/{len(rows)} • {i/len(rows)*100:.1f}% • ETA: {eta}")
        results.append(row)

# === RETRY PASS ===
for r in retry_rows:
    retry_id = try_imdb_lookup(r["Title"])
    r["imdb_id"] = retry_id
    if not retry_id: missing_rows.append(r)

# === EXPORTS ===
with open(progress_output, "w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Title", "imdb_id", "lastepwatched", "status"])
    writer.writeheader()
    for r in results:
        writer.writerow({
            "Title": r["Title"],
            "imdb_id": r["imdb_id"],
            "lastepwatched": r["lastepwatched"],
            "status": "watching" if r["lastepwatched"] else "plan to watch"
        })

if missing_rows:
    with open(missing_output, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(missing_rows)

# === CSV + JSON EXPORT FOR TRAKT HISTORY ===
trakt_fields = ["id", "type", "watched_at", "rating", "rated_at"]
trakt_rows = []
json_rows = []

for r in results:
    imdb = r["imdb_id"]
    if not imdb: continue
    fav = is_favorite(r["Title"], r.get("notes", ""))
    trakt_rows.append({
        "id": f"imdb_id:{imdb}",
        "type": "show",
        "watched_at": now,
        "rating": "10" if fav else "",
        "rated_at": now if fav else ""
    })
    json_row = {
        "imdb_id": imdb,
        "type": "show",
        "watched_at": now
    }
    if fav:
        json_row["rating"] = 10
        json_row["rated_at"] = now
    json_rows.append(json_row)

with open(trakt_output, "w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=trakt_fields)
    writer.writeheader()
    writer.writerows(trakt_rows)

with open(json_output, "w", encoding="utf-8") as f:
    json.dump(json_rows, f, indent=2)
print(f"\n📄 JSON saved: {json_output} ({len(json_rows)} items)")
print(f"📦 CSV saved: {trakt_output}")

# === VERIFY AGAINST TRAKT ===
verified, unverified = [], []
for r in trakt_rows:
    imdb_id = r["id"].split(":")[1]
    if verify_trakt_id(imdb_id): verified.append(r)
    else: unverified.append(r)

with open(verified_output, "w", newline='', encoding="utf-8") as f:
    csv.DictWriter(f, fieldnames=trakt_fields).writerows(verified)
with open(unverified_output, "w", newline='', encoding="utf-8") as f:
    csv.DictWriter(f, fieldnames=trakt_fields).writerows(unverified)

print(f"\n✅ Trakt verified: {len(verified)}")
print(f"🚫 Trakt unverified: {len(unverified)}")