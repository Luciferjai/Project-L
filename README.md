# LILA BLACK — Player Journey Viewer

A browser-based visualization tool for Level Designers to explore player behavior across LILA BLACK's maps. Load any match, watch it unfold on the minimap, track individual player journeys, and identify kill zones, death zones, and high-traffic areas.

**Live tool:** https://project-lilablack.netlify.app/

---

## What It Does

- Plots every player and bot event on the correct minimap with accurate world-to-pixel coordinate mapping
- Distinguishes humans (colored paths) from bots (gray paths) visually
- Shows all 8 event types as distinct colored markers — movement, kills, deaths, loot, storm deaths
- Timeline playback — watch a match unfold second by second with play/pause and speed control
- Heatmap overlays — kill zones, death zones, and traffic density
- Player focus — click any dot or path to isolate one player's full journey
- Match summary panel — players, humans, bots, duration, kills, loot pickups at a glance
- Filter by map, date, and match — with player counts shown upfront so you can pick the richest matches

---

## Project Structure

```
Project-L/
├── backend/
│   ├── main.py          # FastAPI backend — serves data and minimap images
│   └── data.json        # Pre-processed match data (12.5 MB)
├── frontend/
│   └── index.html       # Single-file frontend — all HTML, CSS, JS
├── player_data/
│   └── minimaps/        # Minimap images for all 3 maps
├── ARCHITECTURE.md
├── INSIGHTS.md
├── README.md
└── requirements.txt
```

---

## Running Locally

### Prerequisites
- Python 3.11+
- Git

### Setup

**1. Clone the repo**
```bash
git clone https://github.com/Luciferjai/Project-L.git
cd Project-L
```

**2. Create a virtual environment**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set the data file path**

The backend uses an environment variable to locate `data.json`. On Windows:
```bash
set DATA_FILE=backend\data.json
set MINIMAP_PATH=player_data\minimaps
```

On Mac/Linux:
```bash
export DATA_FILE=backend/data.json
export MINIMAP_PATH=player_data/minimaps
```

**5. Start the backend**
```bash
uvicorn backend.main:app --reload
```

Backend will be running at `http://127.0.0.1:8000`

**6. Open the frontend**

Make sure `frontend/index.html` has this line:
```javascript
const API = "http://127.0.0.1:8000";
```

Then open `frontend/index.html` directly in your browser. The tool will connect to your local backend automatically.

---

## Deployment

| Service | Purpose | URL |
|---|---|---|
| Render (free tier) | Backend API + minimap images | https://lila-black-backend.onrender.com |
| Netlify (free tier) | Frontend static hosting | https://project-lilablack.netlify.app |

The frontend `index.html` in the repo points to the Render backend by default. To run locally, change the `API` constant to `http://127.0.0.1:8000`.

**Note on cold start:** Render's free tier spins down after 15 minutes of inactivity. The splash screen handles this — it polls the backend and shows a loading indicator until the server wakes up (usually 30-50 seconds). UptimeRobot is configured to ping the backend every 5 minutes to prevent sleep during active use.

---

## Regenerating the Data

If new match data is available, re-run the preprocessing script:

```bash
# Update DATA_PATH in the script to point to your player_data folder
python player_data/export_json.py
```

This will regenerate `backend/data.json` from the raw parquet files. Commit and push the new file to redeploy.

---

## Tech Stack

- **Backend:** Python, FastAPI, uvicorn
- **Frontend:** HTML, CSS, JavaScript (no frameworks, no build tools)
- **Map:** Leaflet.js, Leaflet.heat
- **Data:** Apache Parquet → pre-processed JSON
- **Hosting:** Render + Netlify

---

## Recommended Matches for Demo

These matches have the most complete player data across all 3 maps:

| Match ID | Map | Players | Humans | Bots |
|---|---|---|---|---|
| `fbbc5d02-dd79-42fb-bba5-d768023891c8.nakama-0` | AmbroseValley | 16 | 1 | 15 |
| `d0a38c30-d476-4305-857d-ece9e65f72e6.nakama-0` | Lockdown | 15 | 1 | 14 |
| `c46304c9-c9a7-46f1-98e0-ff968930c74b.nakama-0` | GrandRift | 12 | 1 | 11 |

Select **All dates** in the date dropdown and paste the match ID directly into the match search box.
