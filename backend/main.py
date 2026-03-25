import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# ─────────────────────────────────────────
# APP INIT
# ─────────────────────────────────────────
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
# STATIC FILES (minimaps)
# ─────────────────────────────────────────
MINIMAP_PATH = os.getenv(
    "MINIMAP_PATH",
    r"E:\Project L\player_data\minimaps"
)
app.mount("/minimaps", StaticFiles(directory=MINIMAP_PATH), name="minimaps")

# ─────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────
DATA_FILE = os.getenv(
    "DATA_FILE",
    r"E:\Project L\backend\data.json"
)

print(f"Loading data from {DATA_FILE}...")
with open(DATA_FILE, 'r') as f:
    DATA = json.load(f)
print(f"Done. {len(DATA['matches'])} matches, "
      f"{sum(len(v) for v in DATA['events'].values())} events")

# ─────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────
@app.get("/")
def home():
    return {"status": "LILA BLACK backend is running"}

@app.get("/maps")
def get_maps():
    return {"maps": DATA["maps"]}

@app.get("/dates")
def get_dates():
    return {"dates": DATA["dates"]}

@app.get("/matches")
def get_matches(map_id: str = None, date: str = None):
    matches = []
    for mid, info in DATA["matches"].items():
        if map_id and info["map_id"] != map_id:
            continue
        if date and date != "all" and info["day"] != date:
            continue
        matches.append({
            "match_id":     mid,
            "players":      info["players"],
            "humans":       info["humans"],
            "bots":         info["bots"],
            "total_events": info["total_events"],
        })
    matches.sort(key=lambda x: x["players"], reverse=True)
    return {"matches": matches, "count": len(matches)}

@app.get("/events")
def get_events(match_id: str):
    events = DATA["events"].get(match_id)
    if events is None:
        return {"error": "Match not found", "events": [], "total_events": 0}
    return {
        "match_id":     match_id,
        "total_events": len(events),
        "events":       events,
    }