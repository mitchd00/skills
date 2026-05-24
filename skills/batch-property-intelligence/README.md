# batch-property-intelligence

Intelligence Hub for Elite Lifestyle Properties. Watches a folder for RP Data CSV exports,
accumulates everything into SQLite, recomputes ownership + portfolio counts + lead scoring
across the **whole** dataset on every drop, and regenerates a branded master Excel + HTML dashboard.
Backwards-compatible one-shot CLI is still available.

**Status:** V1.2 — Intelligence Hub. SQLite persistence + folder watcher + master dashboard.

---

## Quick start

### 1. Install

```bash
cd batch-property-intelligence
pip install -e .
```

Add dev tools (pytest, pyinstaller) if you want to build the .exe or run tests:

```bash
pip install -e ".[dev]"
```

### 2. Run the launcher (recommended)

```bash
bpi launcher
```

Click **Start Watcher**, then **Pick CSV…** to add your RP Data exports. The dashboard regenerates
automatically as files land in `inputs/`. Click **Open Dashboard** when you're ready to look.

### 3. Or run from the CLI

Start the Hub watcher (blocking):

```bash
bpi watch
```

In another terminal, drop CSVs into `inputs/`. Each one triggers ingest → rescore (across the full DB) → dashboard regen.

One-off ingest without the watcher:

```bash
bpi ingest inputs/Rpdata_Currimundi_May_2026.csv
```

Regenerate the dashboard from the current DB (no new ingest):

```bash
bpi rebuild
```

### 4. One-shot mode (no DB, V1.1 behaviour)

If you want the V1.1 single-run flow with no persistence:

```bash
bpi run \
  --input inputs/Rpdata_Currimundi_May_2026.csv \
  --region "Currimundi May 2026" \
  --output-dir outputs
```

Multi-CSV one-shot run:

```bash
bpi run \
  --input inputs/Rpdata_4551_2026.csv \
  --input inputs/Rpdata_4575_2026.csv \
  --region "SC Combined 4551 + 4575 May 2026"
```

---

## What the Hub produces

### Master dashboard (regenerated on every CSV drop)

- `outputs/BPI_Master_Dashboard_V<N>_<DD-MM-YYYY_HHMM>.xlsx` — six sheets:
  1. **Summary** — top-line counts, lead distribution, top 20 scorers
  2. **All Properties** — every parcel in the DB enriched with scoring columns
  3. **High Priority** — HIGH Seller OR HIGH Rental, sorted by Combined Score
  4. **Portfolios** — owners holding 2+ properties across the whole DB
  5. **Rentals** — confirmed rentals (Owner Type = Rented)
  6. **Filtered Out** — government / reserve / institutional owners (transparency)
- `outputs/BPI_Master_Dashboard_V<N>_<DD-MM-YYYY_HHMM>.html` — single-page scan report (60-second read).
- `outputs/BPI_Master_Dashboard_latest.{xlsx,html}` — fixed-name aliases the launcher opens.
- `outputs/Archive/` — prior versioned files, moved here on each rebuild per ELP archive rule.

### Scoring grades

- **Seller Lead:** HIGH / MEDIUM / LOW / NO
- **Rental Lead:** HIGH / MEDIUM / LOW / NO
- **Combined Lead Score:** 1–10 with a one-line Recommended Action

Full scoring matrices in `references/scoring-tables.md`.

---

## Architecture

```
inputs/<your.csv>                    drop in
        │
        ▼
src.hub.watcher  ────►  src.hub.ingest  ────►  data/bpi.sqlite
                                                       │
                                                       ▼
                                          src.hub.recompute (full DB)
                                                       │
                                                       ▼
                                          src.hub.dashboard
                                                       │
                                                       ▼
                                       outputs/BPI_Master_Dashboard_*
```

- **Hub modules:** `src/hub/{db,ingest,recompute,watcher,dashboard,status}.py`
- **Launcher:** `src/launcher/app.py` (Tkinter, stdlib only)
- **Scoring (unchanged from V1.1):** `src/scoring/{current_owner,portfolio,seller_lead,rental_lead,combined}.py`
- **CSV ingest:** `src/sources/rpdata_csv.py`
- **Output rendering:** `src/output/{excel,html_report}.py`
- **Config:** `config/scoring-weights.yaml`

---

## Configuration

All tuning is in `config/scoring-weights.yaml`:

- `sc_postcodes` — postcodes that count toward SC portfolio counting
- `long_held_years` — threshold for long-held single-property owner = Seller Lead LOW (default 15)
- `recent_purchase_years` — threshold for recent purchase = Seller Lead NO (default 5)
- `entity_patterns` — name fragments that classify owner as Entity (PTY LTD, TRUST, SMSF, …)
- `non_saleable_patterns` — owner name fragments that filter to Non-Saleable (government, churches, aged care, …)
- `non_saleable_land_uses` — land use fragments that filter to Non-Saleable

Edit the YAML, run `bpi rebuild`. No code changes needed.

---

## Windows .exe packaging

For a double-clickable launcher on Mitch's Windows machine:

```powershell
cd build
powershell -File build-windows-exe.ps1
```

Produces `dist/bpi-launcher.exe` (single file, ~30 MB). The PyInstaller spec is at `build/bpi-launcher.spec`.

Build must run on a Windows host — Linux build hosts can't produce Windows binaries without Wine.

---

## ELP folder placement (on Mitch's machine)

```
Projects\ELITE-Project-System\10_Code-Projects\batch-property-intelligence\
```

Outputs default to `./outputs/`. For ELP routing, point the launcher / `--outputs` to:

```
Projects\ELITE-Project-System\07_Cowork-Outputs\Batch-Intelligence-Runs\Master\
```

---

## RP Data export limits — practical guidance

RP Data caps exports at **10,000 records per month**. Suggested rotation:

- **Month 1:** All 4551 sales last 5 years (~5k rows) + all 4575 sales last 5 years (~5k rows). Drop both into `inputs/` — cross-suburb portfolios light up immediately.
- **Month 2:** Owner Search exports on the top 50 scorers from Month 1. Drop into the same `inputs/`. Their wider portfolios merge automatically.
- **Quarterly:** Refresh the main SC exports. Re-drops are idempotent.

---

## Credentials

The Hub stores none. Never embed RP Data, LockedOn, Pricefinder, or Titles Registry passwords.
Authentication for those sources lives in browser sessions, not in this code.

---

## Related ELP skills

- **`property-intelligence-dossier`** — depth layer. Hand off the top 10–15 scorers from the High Priority sheet for full Word + PDF dossiers.
- **`cma-builder`** — invoked from the dossier skill.
- **`lockedon-add-potential-seller`** — invoke after a HIGH Seller Lead is contact-ready.

---

## Phases (forward roadmap)

- **V1** — One-shot CSV ingest + scoring + Excel + HTML. Free. ✅
- **V1.1** — Production hardening. Header auto-detect, "Not Disclosed" handling, extended non-saleable patterns. Free. ✅
- **V1.2 (this build)** — Intelligence Hub. SQLite persistence + folder watcher + master dashboard + Tkinter launcher. Free. ✅
- **V1.3** — Free API enrichment: ABN Lookup, ACNC, ASIC quick search, QLD Globe overlay data.
- **V1.4** — Google Custom Search news mentions + aerial imagery + LockedOn MCP cross-check. ~$15/run.
- **V2** — Gated paid enrichments: ASIC paid extracts ($22/extract), Titles searches ($33/search).
- **V2.1** — Direct handoff to `property-intelligence-dossier` skill for top 10 scorers.

---

## Sources

- `references/bpi-scope.md` — original V1 scope and architecture
- `references/hub-architecture.md` — V1.2 Hub design, schema, watcher loop
- `references/scoring-tables.md` — Seller/Rental/Combined matrices
- `SKILL.md` — Claude-facing trigger doc
