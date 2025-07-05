# 🎌 OtakuSync  
**Watched Anime List Importer for Trakt**

OtakuSync is a Python-powered utility (`trakt-importer.py`) that syncs your anime watchlist directly into Trakt history. It enriches titles using IMDb and Episodate, auto-tags favorites, fills in missing data, and generates Trakt-compatible exports for seamless import.

No more manual logging—just pure anime flow. ⚔️📺

---

## ✨ Features

- 🔍 Enriches anime titles with IMDb IDs and episode info  
- 🧠 Parses formats like `S01E12`, `1x12`, and freeform notes  
- 🏷️ Flags "favorite" entries and auto-rates them 10  
- 🔁 Retry logic for failed lookups  
- ✅ Verifies entries with Trakt’s API  
- 📄 Outputs `.json` and `.csv` for Trakt import  
- 🗂️ Tracks viewing progress and unmatched titles  

---

## 🛠 Requirements

Python 3.7+ recommended.

Install dependencies via:

```bash
pip install imdbpy requests thefuzz
```

Standard library modules used:  
`csv`, `json`, `re`, `datetime`, `time`, `sys`, `threading`, `concurrent.futures`

---

## 🔐 Trakt Setup

OtakuSync requires your personal Trakt Client ID to connect with Trakt’s API.

1. Visit [Trakt Applications](https://trakt.tv/oauth/applications)  
2. Create a new personal app (no redirect URI required)  
3. Copy your **Client ID**  
4. Paste it into `trakt-importer.py`:

```python
TRAKT_CLIENT_ID = "your-client-id-here"
```

---

## 📋 CSV Input Format

Your anime list should be saved as `anime list.csv` with these columns:

| Column | Description |
|--------|-------------|
| `Title` | Required. Name of the anime |
| `lastepwatched` | Optional. Episode info like "S01E10", "1x10", etc. |
| `notes` | Optional. Include `"favorite"` to auto-rate as 10 |

💡 This repo includes a sample `anime list.csv` for reference.

---

## 🚀 How to Run

Once your anime list and Client ID are ready:

```bash
python trakt-importer.py
```

OtakuSync will generate:

| Output File | Purpose |
|-------------|---------|
| `trakt-import.json` | ✅ Trakt watch history import |
| `trakt-import.csv` | Alternative CSV version |
| `watch_progress.csv` | Tracks episode status |
| `missing_ids.csv` | Unresolved IMDb titles |
| `trakt-verified.csv` | Trakt-approved titles |
| `trakt-unverified.csv` | Titles not found by Trakt |

---

## 💖 Favorite Tagging

Any anime with `"favorite"` (case-insensitive) in the `Title` or `notes` column will be:

- Auto-rated `10` in Trakt  
- Stamped with `rated_at`  
- Marked `watched_at` for history import

---

## 📂 Upload to Trakt

Go to [https://trakt.tv/settings/data](https://trakt.tv/settings/data)  
Choose **Import Data > JSON**  
Upload `trakt-import.json`  
Your anime titles will appear in your Trakt watch history.

---

## 🤝 Support & Contributions

OtakuSync is built for fans who crave order, automation, and anime.  
Feel free to fork, star, or submit pull requests for features and improvements!

---

## 🧙 Author

Created by [Brodey]  
Fueled by creativity, strategy, and anime spirit ⚔️✨

---

## 📄 License

Licensed under the MIT License.
