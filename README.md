# 🎌 OtakuSync  
**Watched Anime List Importer for Trakt**

OtakuSync is a Python-powered utility (`trakt-importer.py`) that transforms your anime watchlist into a Trakt watch history. It enriches titles using IMDb and Episodate, auto-tags favorites, fills in missing data, and exports your anime library into Trakt-compatible formats—ready for clean, instant import.

---

## 📦 Features

- 🔍 Enriches anime titles with episode info and IMDb IDs
- 🧠 Automatically parses `SxxExx`, `1x12`, or freeform episodes
- 🏷️ Flags entries with "favorite" for Trakt auto-rating (10)
- 🔁 Includes retry logic for failed IMDb lookups
- ✅ Verifies IMDb IDs against Trakt's database
- 📄 Exports both `.json` and `.csv` for Trakt import
- 🗂️ Tracks watch status and separates unmatched titles

---

## 🛠 Requirements

Python 3.7+ recommended.

Install dependencies via:

```bash
pip install imdbpy requests thefuzz
```

Standard library modules used:
- `csv`, `json`, `re`, `datetime`, `time`, `sys`, `threading`, `concurrent.futures`

---

## 🔐 Setup: Trakt Client ID

OtakuSync connects with Trakt’s API using your personal Client ID.

1. Go to [Trakt Applications](https://trakt.tv/oauth/applications)
2. Create a new app (no redirect URI required)
3. Copy your **Client ID**
4. Paste it into `trakt-importer.py` like this:

```python
TRAKT_CLIENT_ID = "your-client-id-here"
```

---

## 📋 Input Format

Your anime list should be a CSV file named `anime list.csv` with the following columns:

- `Title` — Required. The name of the anime.
- `lastepwatched` — Optional. Episode or season info (e.g. "S01E12", "1x12", etc.)
- `notes` — Optional. Use `"favorite"` to auto-rate shows as 10.

💡 A sample file `anime list.csv` is included in this repo to use as a template.

---

## 🚀 How to Use

Once you've added your anime list and Trakt Client ID:

```bash
python trakt-importer.py
```

OtakuSync will process your entries and generate the following output:

| File | Purpose |
|------|---------|
| `trakt-import.json` | ✅ For Trakt watch history importer |
| `trakt-import.csv` | Alternative CSV version (for manual use) |
| `watch_progress.csv` | Local tracker for status and last episode |
| `missing_ids.csv` | Titles with unresolved IMDb entries |
| `trakt-verified.csv` | Confirmed titles accepted by Trakt |
| `trakt-unverified.csv` | Titles rejected by Trakt’s database |

---

## 🧾 How Favorites Work

Any anime with the word `favorite` (case-insensitive) in the `Title` or `notes` column will:

- Be rated `10` in Trakt
- Include a `rated_at` timestamp
- Be marked as `watched_at` to appear in your watch history

---

## 📂 JSON Upload Instructions

Go to [Trakt Import: History](https://trakt.tv/users/import/export/history)  
Upload `trakt-import.json`  
Your anime titles will appear in your watched history with ratings and timestamps.

---

## ❤️ Support & Contributions

OtakuSync is made for anime fans who crave clean organization, historical tracking, and seamless syncing with Trakt.

Feel free to fork this project, submit pull requests, or tweak it to your own workflow. Future enhancements welcome!

---

## 🧙‍♂️ Author

Created by [Brodey]  
Built with creativity, strategy, and a touch of anime spirit ⚔️✨

---

## 📄 License

This project is licensed under the MIT License.
