---
name: batch-property-intelligence
description: Intelligence Hub for Australian residential property research at Elite Lifestyle Properties. Watches an `inputs/` folder for RP Data CSV exports, accumulates everything into a SQLite database, recomputes current ownership + portfolio counts + Seller Lead / Rental Lead / Combined (1–10) scoring across the **entire accumulated dataset** on every drop, and regenerates a single branded master Excel + HTML dashboard. Volume layer of the ELP research stack — feeds property-intelligence-dossier for deep workups on the top scorers. Ships with a Tkinter launcher (packageable as a Windows .exe via PyInstaller) so Mitch can start/stop the watcher, pick CSVs, and open the dashboard with one click. Use whenever Mitch asks to "rank these properties", "score this RP Data export", "find the seller leads in this CSV", "who's got a portfolio in [suburb]", "run batch intelligence on [region]", "pull the rentals out of this list", "rebuild the dashboard", "open the BPI hub", or uploads one or more RP Data CSVs. Also trigger on informal phrasings — "score this lot", "rank these", "who looks like a seller", "give me the high priority list", "drop this in the hub".
---

# Batch Property Intelligence — ELP Intelligence Hub

Production skill that wraps the `batch-property-intelligence` Python project as a long-running Intelligence
Hub. Two parts:

- **Hub** — `bpi watch` runs a folder watcher (`watchdog`) on `inputs/`. Every CSV dropped in is ingested
  into `data/bpi.sqlite`, scores are recomputed across the **whole accumulated DB**, and the master
  dashboard is regenerated at `outputs/BPI_Master_Dashboard_V<N>_<DD-MM-YYYY_HHMM>.{xlsx,html}`.
- **Launcher** — `bpi launcher` (or the PyInstaller-built `bpi-launcher.exe`) opens a Tkinter window with
  start/stop/pick/open-dashboard buttons.

Backwards-compatible one-shot mode (`bpi run`) is still available for stateless single-CSV runs.

## When to invoke this skill

| Mitch says / does | Action |
|---|---|
| Uploads an RP Data CSV in a chat | Copy the CSV into the Hub's `inputs/` folder (the watcher picks it up), or run `bpi ingest <csv>` directly. Open the dashboard when done. |
| "Rank/score these properties" with a CSV attached | Same as above. |
| "Run batch intelligence on Currimundi May 2026" with a CSV path | `bpi ingest <csv>` then `bpi rebuild` (or rely on watcher). |
| "Who's got a portfolio in 4551?" | Confirm the latest 4551 export has been ingested; if so, point to the Portfolios sheet of `BPI_Master_Dashboard_latest.xlsx`. If not, ask for the export first. |
| "Find the seller leads / rentals" | Same as above — direct Mitch to the High Priority or Rentals sheet. |
| "Open the hub" / "Start the hub" | `bpi launcher` to open the window, or `bpi watch` to start the watcher directly. |
| "Rebuild the dashboard" | `bpi rebuild` — recomputes scores across the DB and regenerates the master Excel + HTML. No ingest needed. |
| "Status?" | `bpi status` — prints JSON with watcher state and DB counts. |

## Install

From the skill folder:

```bash
pip install -e .            # production
pip install -e ".[dev]"     # adds pytest + pyinstaller
```

`bpi` and `bpi-launcher` scripts are registered on the PATH.

## CLI

```
bpi run       --input <csv> [--input <csv2> ...] --region <label> [--output-dir <dir>]   # one-shot (no DB)
bpi watch     [--inputs <dir>] [--outputs <dir>] [--data <db>] [--config <yaml>]         # blocking Hub watcher
bpi ingest    <csv> [--data <db>] [--no-rebuild]                                          # one-off ingest
bpi rebuild   [--data <db>] [--outputs <dir>]                                             # regen dashboard from DB
bpi launcher                                                                              # Tkinter window
bpi status    [--data <db>]                                                               # JSON status + DB counts
```

## Hub flow (every CSV drop)

1. `watchdog` fires `on_created`/`on_modified` for a `*.csv` in `inputs/`. 1.5s debounce settles partial writes.
2. `src.hub.ingest.ingest_csv` reads it via the existing `src.sources.rpdata_csv.load_csv` (handles BOM,
   Wurtulla-preamble vs Currimundi-direct headers, "Not Disclosed" sale prices). Upserts into `parcels` +
   `sales`. Inserts a `runs` audit row. Re-dropping the same CSV is idempotent — `sales` PK is
   `(parcel_key, sale_date, sale_price, owner1)`.
3. `src.hub.recompute.recompute_all` rebuilds `parcel_current_owner` and `owners_canonical` across the **whole
   DB**, reusing the unchanged scoring modules (`src.scoring.*`).
4. `src.hub.dashboard.regenerate_dashboard` archives the prior versioned files into `outputs/Archive/`,
   writes `BPI_Master_Dashboard_V<N>_<DD-MM-YYYY_HHMM>.{xlsx,html}`, and refreshes the
   `BPI_Master_Dashboard_latest.{xlsx,html}` aliases the launcher button opens.
5. `data/status.json` is updated. The launcher polls it every 1s.

## SQLite schema (overview)

| Table | Purpose |
|---|---|
| `parcels` | One row per parcel, keyed by `street_address|suburb|state|postcode`. Holds property attributes. |
| `sales` | Every sale event ever ingested. PK prevents duplicates on re-ingest. |
| `runs` | Audit log of every CSV ingested — file name, row count, delta counts, timestamp. |
| `owners_canonical` | Per-owner rollup, recomputed every run: portfolio + rental counts + lead grades. |
| `parcel_current_owner` | Current owner per parcel after latest-sale derivation. |

Full schema in `src/hub/db.py`; architecture notes in `references/hub-architecture.md`.

## Outputs

- `outputs/BPI_Master_Dashboard_V<N>_<DD-MM-YYYY_HHMM>.xlsx` — six sheets:
  Summary, All Properties, High Priority, Portfolios, Rentals, Filtered Out.
- `outputs/BPI_Master_Dashboard_V<N>_<DD-MM-YYYY_HHMM>.html` — single-page scan report.
- `outputs/BPI_Master_Dashboard_latest.{xlsx,html}` — copies of the most recent versioned pair.
- `outputs/Archive/…` — prior versions, per ELP archive rule.

## Hard rules (ELP)

1. **Australian spelling.** Colour, organise, metre, realise.
2. **Naming convention.** `<Name>_V<N>_<DD-MM-YYYY_HHMM>.<ext>` on every output.
3. **Archive rule.** Prior versioned files moved to `outputs/Archive/` before the new one is written — never overwrite.
4. **No credentials.** The Hub never accepts RP Data, LockedOn, Pricefinder, or Titles Registry passwords. Authentication for those sources lives in browser sessions, not in this code.
5. **No invented facts.** Lead grades reflect what's actually in the ingested data. Unknown owner type → Rental Lead falls through to LOW or NO, never invented.
6. **OneDrive routing (when deployed on Mitch's machine).** Outputs at `Projects\ELITE-Project-System\07_Cowork-Outputs\Batch-Intelligence-Runs\Master\`. Override with `--outputs`.

## Scoring summary

- **Seller Lead:** HIGH / MEDIUM / LOW / NO based on Owner SC Property Count, Entity vs Individual, years held, owner type.
- **Rental Lead:** HIGH / MEDIUM / LOW / NO based on Owner Type + portfolio rental count.
- **Combined:** 1–10 with a one-line Recommended Action.

Full matrices in `references/scoring-tables.md`. Tunable thresholds + non-saleable patterns in
`config/scoring-weights.yaml`.

## Related ELP skills

- **`property-intelligence-dossier`** — hand off the top 10–15 scorers from the High Priority sheet for full Word + PDF dossiers.
- **`cma-builder`** — invoked from the dossier skill, not directly from BPI.
- **`lockedon-add-potential-seller`** — invoke after a HIGH Seller Lead is contact-ready.

## Reference files

- `references/bpi-scope.md` — V1 scope and architecture (original document)
- `references/hub-architecture.md` — Hub-specific design: DB schema diagram, watcher loop, regen cadence
- `references/scoring-tables.md` — Seller/Rental/Combined matrices, entity patterns, non-saleable patterns

## Windows .exe packaging

For a double-clickable launcher on Mitch's Windows machine:

```powershell
cd build
powershell -File build-windows-exe.ps1
```

Produces `dist/bpi-launcher.exe` (single file, ~30 MB, no Python install needed on the target machine).
The PyInstaller spec lives at `build/bpi-launcher.spec`.

This skill ships the spec and PowerShell driver only — the .exe must be built on a Windows host
(Linux build hosts can't produce Windows binaries without Wine + extra tooling).

## Test plan

```bash
pytest tests/
```

Three tests in `tests/`:

1. `test_scoring.py` — unit tests on the scoring matrix and entity classifier.
2. `test_ingest.py` — synthetic CSV → DB upsert determinism, re-ingest idempotency.
3. `test_recompute.py` — two-CSV cross-suburb ingest, asserts portfolio count of 2 for an owner appearing in both.
