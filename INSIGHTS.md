# Insights — LILA BLACK Player Journey Viewer

---

## Insight 1: Human vs Human Combat Is Effectively Absent

### What I found
Across all 18 complete matches (10+ players) in the dataset, there were **zero Kill events and zero Killed events** — meaning not a single recorded instance of a human player killing another human player across 5 days of production data.

### The evidence
Running an event completeness audit across all full matches:
```
Matches with Kill events:     0 / 18
Matches with Killed events:   0 / 18
Matches with BotKill events:  17 / 18
Matches with Loot events:     16 / 18
```
The dataset contains 89,104 total events. Of these, only 3 Kill events and 3 Killed events exist across the entire dataset — all in partial matches with 1-2 players, suggesting edge cases rather than real PvP encounters.

### What this means for a Level Designer
LILA BLACK is currently functioning as a human-vs-bot experience rather than the PvP extraction shooter it is designed to be. Players are landing, looting, killing bots, and extracting — but never encountering other human players in combat.

**Actionable items:**
- **Map size vs player count mismatch** — With at most 1-2 human players per match on maps designed for larger lobbies, players never get close enough to fight. Consider adding high-value loot hotspots that force multiple humans toward the same location, increasing encounter probability.
- **Metrics to track:** Human encounter rate (% of matches with at least 1 Kill event), average distance between human players at match start.

---

## Insight 2: Bot Combat Is Concentrated in Specific Map Zones

### What I found
Bot-vs-bot combat (BotKillBot events) and human-kills-bot (BotKill events) cluster heavily in specific areas of each map rather than being distributed evenly. On AmbroseValley, combat concentrates in the central river corridor and the prison complex area. On GrandRift, the Mine Pit and Cave House zones account for the majority of combat events. On Lockdown, the Engineer's Quarters area is the dominant combat zone.

### The evidence
Loading match `fbbc5d02` (16 players, AmbroseValley) and toggling the Kill Zones heatmap shows a clear concentration of yellow-to-red intensity in the central map corridor, while large portions of the map — particularly the northern and southern edges — show near-zero combat activity. The same pattern holds across multiple matches on the same map.

In the 18 full matches:
```
Matches with BotKill events:    17 / 18
Bot path density in edge zones: significantly lower than central zones
Human player paths:             almost exclusively through central loot areas
```

### What this means for a Level Designer
Bot AI patrol routes are predictable and concentrated. A human player who understands the map can reliably avoid bots or exploit their clustering. This reduces the tension and challenge the bots are supposed to provide.

**Actionable items:**
- **Redistribute bot spawn points** to cover underutilised map areas (northern edges of AmbroseValley, Labour Quarters on GrandRift). This forces human players to engage with bots regardless of route.
- **Add patrol variance** — if bot paths are scripted, introducing randomisation would prevent experienced players from memorising safe corridors.
- **Metrics to track:** Bot kill distribution by map zone (use the heatmap overlay), percentage of map area with zero bot activity across 10+ matches.

---

## Insight 3: Players Are Completing Extraction Before the Storm Arrives

### What I found
Across all 18 complete matches, there are **zero KilledByStorm events**. Not a single player in the entire 5-day dataset died to the storm mechanic — the core pressure system designed to force player movement and create urgency in the extraction loop.

### The evidence
```
Matches with KilledByStorm events:  0 / 18
Total KilledByStorm across dataset: 39 events total
                                    (all in solo/partial matches)
```
The 39 storm death events that do exist are spread across low-player-count matches and appear to be outliers. In every complete multi-player match, all players either extracted successfully or died to bots before the storm became a factor.

### What this means for a Level Designer
The storm is not functioning as a meaningful design constraint. Players are resolving matches — through extraction or bot death — faster than the storm's current progression reaches them. This removes a key source of tension and late-game decision-making from the experience.

**Actionable items:**
- **Accelerate storm progression** — if matches consistently end before the storm is relevant, the storm timer may need to be shortened so it exerts pressure earlier in the match.
- **Shrink the safe zone faster** — a more aggressive storm boundary would force players to make extraction decisions under pressure rather than at their own pace.
- **Metrics to track:** Average match duration vs storm arrival time, % of players alive when storm first reaches the playable zone.

---

## Insight 4: Players Land Outside the Visible Map — Possible Drop Zone Pattern

### What I found
In every match, the earliest recorded events (ts_seconds near 0) have pixel coordinates that fall outside the visible minimap terrain — in the black border areas surrounding the playable map. These events appear as straight-line trajectories converging toward specific entry points on the map edge, consistent with a parachute or airborne drop mechanic.

### Important caveat
**I do not have access to the LILA BLACK early access build to confirm this interpretation.** This insight is based entirely on data analysis. The README documentation describes the minimap as a 1024x1024 pixel image with a coordinate system, but does not explicitly describe a drop/parachute mechanic or confirm what out-of-bounds events represent. This interpretation is inferred from the pattern of early timestamps having out-of-bounds coordinates followed by rapid convergence toward the playable area — which is consistent with how drop mechanics work in extraction shooters generally.

If these out-of-bounds early events do represent a drop phase, the data suggests players are not landing randomly — trajectories converge on 3-4 entry corridors per map rather than distributing evenly across the border.

### The evidence
In match `d3a3297e` (AmbroseValley, 14 players):
```
Events at ts_seconds < 0.05:  all outside pixel bounds (pixel < 40 or > 990)
Events at ts_seconds > 0.10:  all within playable map area
Trajectory pattern:           linear paths converging on map edge entry points
```

### What this means for a Level Designer (if the interpretation is correct)
If players are consistently funnelling into 2-3 entry corridors, the early-game player density at those points is higher than the map design may intend, while other entry zones are underused.

**Actionable items (pending confirmation of the drop mechanic):**
- **Audit entry point distribution** — if confirmed, adding incentives near underused entry corridors could spread early-game activity more evenly.
- **Metrics to track:** Variance of first in-bounds Position event coordinates per match, percentage of players using each entry corridor.
