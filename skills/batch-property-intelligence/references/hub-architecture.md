# BPI Hub — Architecture (V1.2)

Reference for the Intelligence Hub mode added in V1.2. The Hub turns the one-shot V1.1 CLI into a
long-running watcher backed by a SQLite history.

## Components

| Module | Role |
|---|---|
| `src/hub/db.py` | SQLite schema + connect helper + key normalisation + stats query. |
| `src/hub/ingest.py` | Load one CSV via `src.sources.rpdata_csv.load_csv`, upsert `parcels` + insert `sales`, write a `runs` audit row. |
| `src/hub/recompute.py` | Hydrate a sales-history dataframe from the whole DB, run the unchanged `src.scoring.*` modules, rebuild `parcel_current_owner` + `owners_canonical`. |
| `src/hub/dashboard.py` | Archive prior versioned files, write the new `BPI_Master_Dashboard_V<N>_*.{xlsx,html}`, refresh `_latest` aliases. |
| `src/hub/watcher.py` | `watchdog` Observer; chains ingest → recompute → dashboard → status. |
| `src/hub/status.py` | Tiny JSON status file polled by the launcher. |
| `src/launcher/app.py` | Tkinter window (start/stop/pick/open/rebuild/quit). |

## SQLite schema

```sql
parcels (
  parcel_key PRIMARY KEY,
  street_address, suburb, state, postcode,
  council_area, property_type,
  bed, bath, car, land_size_m2, floor_size_m2, year_built,
  land_use, development_zone, parcel_details, full_address, open_in_rpdata,
  first_seen_at, last_seen_at
)

sales (
  parcel_key, sale_date, sale_price,             -- composite PK with owner1
  settlement_date, sale_type, agency, agent,
  owner1, owner2, owner3, owner_type,
  vendor1, vendor2, vendor3,
  source_csv, source_run_id,
  PRIMARY KEY (parcel_key, sale_date, sale_price, owner1)
)

runs (
  run_id PRIMARY KEY,
  ingested_at, source_csv, row_count,
  new_parcels, new_sales,
  region_hint
)

owners_canonical (
  owner_key PRIMARY KEY,
  display_name, is_entity, is_filtered, filter_reason,
  property_count, rental_count,
  seller_lead, rental_lead, combined_score,
  recommended_action,
  last_recomputed_at
)

parcel_current_owner (
  parcel_key PRIMARY KEY,
  owner_key,
  derived_at
)
```

### Keys

- `parcel_key = upper(street_address) | upper(suburb) | upper(state) | postcode`
- `owner_key = upper(name) with collapsed whitespace`

Both are computed in `src/hub/db.py`.

### Idempotency

The `sales` composite primary key means re-dropping the same CSV inserts no duplicate rows.
`INSERT OR IGNORE` is used for sales; parcels use `ON CONFLICT … DO UPDATE` to refresh attributes (in case
RP Data corrects bed/bath/land size between exports).

`owners_canonical` and `parcel_current_owner` are wiped and rebuilt on every recompute. They're derived
state — never edited by hand.

## Watcher loop

1. `Observer` watches `inputs/` (non-recursive) for `*.csv` create/modify events.
2. Per-file debounce: 1.5s after the last event before processing. Cancels and reschedules if more events
   arrive — handles Chrome's incremental writes during download.
3. On fire:
   - `write_status(state="processing", last_event="Processing <name>")`
   - `ingest_csv(path, db_path)` — returns `{run_id, rows_in_csv, new_parcels, new_sales}`.
   - `recompute_all(db_path, config_path)` — returns the scored dataframe + summary stats.
   - `regenerate_dashboard(df_final, outputs_dir)` — bumps version, archives prior, writes new files.
   - `write_status(state="idle", last_event=<summary>, db_stats=…)`.
4. Existing CSVs in `inputs/` at startup are processed once each (in alphabetical order) before entering
   the event loop.

## Recompute cadence

Every ingest triggers a full recompute. At ~7,000 rows the recompute is sub-second in pandas; this stays
fine well into the tens of thousands. If the DB ever grows to where this becomes painful (~100k+ sales),
move to incremental owner updates — track which owners' portfolios changed in this ingest, rescore only
those. Not needed at any realistic SC scale.

## Output naming

- Versioned: `BPI_Master_Dashboard_V<N>_<DD-MM-YYYY_HHMM>.{xlsx,html}` — `<N>` increments per regen, never overwrites.
- Latest: `BPI_Master_Dashboard_latest.{xlsx,html}` — copies (not symlinks, so they work on Windows).
- Archive: prior versioned files moved to `outputs/Archive/` before the new pair lands.

## Launcher ↔ Hub IPC

Deliberately simple — files, not sockets:

- Launcher spawns `python -m src.main watch` as a subprocess; PID stored in `data/watcher.pid`.
- Watcher writes `data/status.json` on every state transition.
- Watcher writes `data/bpi.log` (rolling) — launcher tails the last 20 lines.
- Launcher polls `status.json` and the log every 1s. No locking; eventual consistency is fine.

## Configuration

`config/scoring-weights.yaml` is loaded on every recompute. Edit it and run `bpi rebuild` to apply.
No code changes needed for new non-saleable patterns, entity patterns, postcode coverage, or thresholds.

## What's deliberately not implemented in V1.2

- Web dashboard / HTTP server — file-based outputs only.
- Multi-machine sync of the SQLite DB — single-machine. (Could be served by putting `data/` on OneDrive
  with file locking caveats.)
- Incremental owner recompute — full rebuild every run while it's cheap.
- Drag-and-drop in the Tkinter window — `tkinterdnd2` dependency avoided to keep the .exe simple. Use
  the "Pick CSV…" button instead.
