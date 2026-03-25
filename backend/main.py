from fastapi import FastAPI

app = FastAPI()
from fastapi.staticfiles import StaticFiles

app.mount("/minimaps", StaticFiles(directory=r"E:\Project L\player_data\minimaps"), name="minimaps")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "LILA Backend is running"}
import os
import pandas as pd
import pyarrow.parquet as pq

DATA_PATH = os.getenv("DATA_PATH", r"E:\Project L\player_data")

def world_to_pixel(x, z, map_id):
    configs = {
        'AmbroseValley': {'scale': 900,  'ox': -370, 'oz': -473},
        'GrandRift':     {'scale': 581,  'ox': -290, 'oz': -290},
        'Lockdown':      {'scale': 1000, 'ox': -500, 'oz': -500},
    }
    c = configs[str(map_id)]
    u = (x - c['ox']) / c['scale']
    v = (z - c['oz']) / c['scale']
    return round(u * 1024), round((1 - v) * 1024)

def load_all_data():
    frames = []
    for day_folder in os.listdir(DATA_PATH):
        day_path = os.path.join(DATA_PATH, day_folder)
        if not os.path.isdir(day_path):
            continue
        for filename in os.listdir(day_path):
            filepath = os.path.join(day_path, filename)
            try:
                t = pq.read_table(filepath)
                frame = t.to_pandas()
                frame['event'] = frame['event'].apply(
                    lambda x: x.decode('utf-8') if isinstance(x, bytes) else x
                )
                frame['day'] = day_folder
                frames.append(frame)
            except Exception as e:
                continue
    return pd.concat(frames, ignore_index=True)


def load_all_data():
    frames = []
    for day_folder in os.listdir(DATA_PATH):
        day_path = os.path.join(DATA_PATH, day_folder)
        if not os.path.isdir(day_path):
            continue
        for filename in os.listdir(day_path):
            filepath = os.path.join(day_path, filename)
            try:
                t = pq.read_table(filepath)
                frame = t.to_pandas()
                frame['event'] = frame['event'].apply(
                    lambda x: x.decode('utf-8') if isinstance(x, bytes) else x
                )
                frame['day'] = day_folder
                frames.append(frame)
            except Exception as e:
                continue
    df = pd.concat(frames, ignore_index=True)

    # Detect bots from user_id — numeric ID = bot, UUID = human
    df['is_bot'] = df['user_id'].apply(
        lambda uid: str(uid).replace('-', '').isnumeric() or not '-' in str(uid)
    )
    return df

print("Loading all data... this may take 30 seconds")
df = load_all_data()
print(f"Done. Loaded {len(df)} total rows")
@app.get("/maps")
def get_maps():
    maps = df['map_id'].astype(str).unique().tolist()
    return {"maps": maps}
@app.get("/dates")
def get_dates():
    dates = sorted(df['day'].unique().tolist())
    return {"dates": dates}
@app.get("/matches")
def get_matches(map_id: str = None, date: str = None):
    filtered = df.copy()
    if map_id:
        filtered = filtered[filtered['map_id'].astype(str) == map_id]
    if date and date != "all":
        filtered = filtered[filtered['day'] == date]

    # Group by match and count players
    match_info = filtered.groupby('match_id').agg(
        total_events = ('event', 'count'),
        unique_players = ('user_id', 'nunique'),
        human_players = ('user_id', lambda x: x[filtered.loc[x.index, 'is_bot'] == False].nunique()),
        bot_players   = ('user_id', lambda x: x[filtered.loc[x.index, 'is_bot'] == True].nunique()),
    ).reset_index()

    # Sort by player count descending
    match_info = match_info.sort_values('unique_players', ascending=False)

    matches = [
        {
            "match_id":      row['match_id'],
            "players":       int(row['unique_players']),
            "humans":        int(row['human_players']),
            "bots":          int(row['bot_players']),
            "total_events":  int(row['total_events']),
        }
        for _, row in match_info.iterrows()
    ]

    return {"matches": matches, "count": len(matches)}


@app.get("/events")
def get_events(match_id: str):
    # Try exact match first
    match_df = df[df['match_id'].astype(str) == match_id].copy()

    # If empty, try matching without .nakama-0 suffix
    if match_df.empty:
        base_id = match_id.replace('.nakama-0', '')
        match_df = df[df['match_id'].astype(str).str.contains(base_id)].copy()

    if match_df.empty:
        return {"error": "Match not found", "events": [], "total_events": 0}

    print(f"Match {match_id}: found {len(match_df)} rows, {match_df['user_id'].nunique()} unique players")

    match_df[['pixel_x', 'pixel_y']] = match_df.apply(
        lambda row: pd.Series(world_to_pixel(row['x'], row['z'], row['map_id'])),
        axis=1
    )

    match_df['ts_seconds'] = (
        (match_df['ts'] - match_df['ts'].min())
        .dt.total_seconds()
    )

    events = match_df[[
        'user_id', 'event', 'pixel_x', 'pixel_y',
        'ts_seconds', 'is_bot', 'map_id'
    ]].to_dict(orient='records')

    return {
        "match_id": match_id,
        "total_events": len(events),
        "events": events
    }
@app.get("/debug")
def debug_match(match_id: str):
    base_id = match_id.replace('.nakama-0', '')
    matches = df[df['match_id'].astype(str).str.contains(base_id)]['match_id'].unique().tolist()
    return {"found_match_ids": matches, "count": len(matches)}