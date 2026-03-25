# Architecture — LILA BLACK Player Journey Viewer

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Data processing | Python, pandas, pyarrow | Native parquet support, fast dataframe operations |
| Backend | FastAPI (Python) | Lightweight, fast, auto-generates API docs, easy to run locally |
| Frontend | Plain HTML + JavaScript | No build tools needed, fast to iterate, works anywhere |
| Map rendering | Leaflet.js | Best-in-class for custom image overlays and marker layers |
| Heatmaps | Leaflet.heat plugin | One script tag, works natively with Leaflet |
| Backend hosting | Render (free tier) | No credit card, deploys from GitHub, Python native support |
| Frontend hosting | Netlify (free tier) | Instant static hosting, auto-deploys on git push |
| Version control | GitHub | Standard, integrates with both Render and Netlify |

---

## Data Flow

```
Raw parquet files (1,243 files, 5 days)
        |
export_json.py (local preprocessing script)
  - Loads all parquet files via pyarrow
  - Decodes event column from bytes to UTF-8 strings
  - Detects bots vs humans from user_id format (UUID = human, numeric = bot)
  - Converts world coordinates (x, z) to minimap pixel coordinates (pixel_x, pixel_y)
  - Normalizes timestamps per match to ts_seconds from match start
  - Groups events by match_id
  - Outputs single data.json (12.5 MB)
        |
data.json (committed to GitHub repo)
        |
FastAPI backend (Render)
  - Loads data.json into memory on startup
  - Serves 4 endpoints: /maps, /dates, /matches, /events
  - Serves minimap images as static files via /minimaps
        |
Frontend (Netlify - browser)
  - Splash screen polls backend until ready (handles cold start)
  - Dropdowns populated from /maps and /dates
  - Match list loaded from /matches with player counts
  - On Load Match fetches /events and renders markers on Leaflet map
  - Timeline slider filters events by ts_seconds
  - Heatmap overlays built from event coordinates using Leaflet.heat
```

---

## Coordinate Mapping Approach

The game world uses a 3D coordinate system (x, y, z). For 2D minimap plotting:

- **y is ignored** — it represents elevation, irrelevant for top-down view
- **x and z** are used for the 2D position

Each map has a known scale and origin (from the game's configuration):

```
AmbroseValley: scale=900,  origin=(-370, -473)
GrandRift:     scale=581,  origin=(-290, -290)
Lockdown:      scale=1000, origin=(-500, -500)
```

Conversion to pixel coordinates on the 1024x1024 minimap image:

```python
u = (x - origin_x) / scale          # normalize to 0-1
v = (z - origin_z) / scale          # normalize to 0-1
pixel_x = u * 1024
pixel_y = (1 - v) * 1024            # Y flipped - image origin is top-left
```

The Y flip is critical — game world Z increases upward, image Y increases downward.

Validated against README example:
- Input: x=-301.45, z=-355.55 (AmbroseValley)
- Expected output: pixel (78, 890)
- Actual output: pixel (78, 890) confirmed

---

## Assumptions

| Situation | Assumption Made |
|---|---|
| Bot detection | User IDs without hyphens (numeric) are bots; UUIDs are humans. Confirmed by README. |
| Timestamps | ts column represents time elapsed within a match context, not wall-clock time. Normalized per match by subtracting the minimum ts value in that match. |
| Drop zone events | Events at ts_seconds near 0 with pixel coordinates outside the map bounds represent the parachute/drop phase before landing. These are valid data points not errors. |
| BotKill/BotKilled on bot entities | When these events appear on bot user IDs, they represent bot-vs-bot combat, reclassified as BotKillBot in the frontend for clarity. |
| February 14 data | Partial day as noted in README — lower event counts are expected. |
| Match completeness | 743 of 796 matches have only 1 player file captured. Only 18 matches have 10+ players. Analysis focused on these 18 complete matches. |

---

## Trade-offs

| Decision | What I chose | What I traded off |
|---|---|---|
| JSON vs live parquet pipeline | Pre-processed JSON file | Lost real-time data updates; gained free hosting and faster startup |
| Plain HTML vs React/Vue | Plain HTML + JS | Less component reusability; gained zero build complexity and faster iteration |
| Leaflet vs Deck.gl | Leaflet.js | Less GPU-accelerated rendering; gained simpler setup and better image overlay support |
| Single data.json vs per-match files | Single file (12.5MB) | Slightly larger initial load; gained simpler backend with no file I/O per request |
| Render free tier vs paid | Free tier | Cold start delay on inactivity; gained zero cost for evaluation period |

---

## Handling the Render Free Tier Cold Start

Render's free tier spins down services after 15 minutes of inactivity, causing a 30-50 second cold start delay on the next request. Two measures were added to handle this:

**1. Frontend splash screen** — Instead of showing a broken or empty UI during cold start, the frontend displays a full-screen splash screen with an animated loading indicator. It silently polls the backend every 5 seconds and automatically dismisses once the backend responds. The message updates to show elapsed wait time so the user knows the server is waking up and hasn't crashed.

**2. UptimeRobot keep-alive** — A free UptimeRobot monitor pings the backend every 5 minutes, preventing it from sleeping during active use periods. This eliminates the cold start delay entirely as long as the tool has been accessed recently.

---

## What I'd Do Differently With More Time

1. **Real-time data pipeline** — Replace the pre-processed JSON with a proper data store (DuckDB or PostgreSQL). New match data could be ingested automatically without re-running the export script.

2. **WebSocket playback** — Instead of client-side timeline filtering, stream events from the backend in real time for smoother match playback.

3. **Per-map coordinate calibration UI** — Let Level Designers fine-tune the origin and scale values visually if the game map changes, rather than hardcoding them.

4. **Player clustering analysis** — Add server-side spatial clustering (DBSCAN) to automatically identify hot zones rather than relying on heatmap interpretation.

5. **Multi-match comparison** — Let Level Designers overlay two matches simultaneously to compare player behaviour across different sessions on the same map.
