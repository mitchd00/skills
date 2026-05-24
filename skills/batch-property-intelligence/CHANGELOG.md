# Changelog

## V1.2 — Intelligence Hub

Pivot from one-shot CLI to a long-running Intelligence Hub. The empty `src/cache/db.py` slot reserved
in the V1 scope is now the engine.

### Added

- **SQLite persistence** (`src/hub/db.py`) — `parcels`, `sales`, `runs`, `owners_canonical`,
  `parcel_current_owner` tables. Schema is idempotent; re-ingesting the same CSV inserts no duplicate rows
  thanks to the `sales` composite PK `(parcel_key, sale_date, sale_price, owner1)`.
- **Folder watcher** (`src/hub/watcher.py`) — `watchdog` Observer with a 1.5s debounce. On each CSV drop:
  ingest → full-DB recompute → dashboard regen → status update.
- **CSV ingest** (`src/hub/ingest.py`) — reuses the existing `src.sources.rpdata_csv.load_csv` for
  header auto-detection, BOM handling, and price/date parsing.
- **Cross-DB recompute** (`src/hub/recompute.py`) — rebuilds current-owner derivation, portfolio counting,
  and lead scoring across the entire accumulated dataset every run. Cross-suburb portfolios light up
  automatically once enough CSVs have been ingested.
- **Master dashboard** (`src/hub/dashboard.py`) — `outputs/BPI_Master_Dashboard_V<N>_<DD-MM-YYYY_HHMM>.{xlsx,html}`
  with `_latest` aliases for the launcher button. Archives prior versioned files into `outputs/Archive/`
  per ELP rule.
- **Status file** (`src/hub/status.py`) — small JSON at `data/status.json` polled by the launcher.
- **Tkinter launcher** (`src/launcher/app.py`) — stdlib-only window with Start/Stop/Pick/Open Dashboard/
  Rebuild buttons, status pane, and log tail.
- **New CLI subcommands** (`src/main.py`): `watch`, `ingest`, `rebuild`, `launcher`, `status`. The V1.1
  `run` subcommand stays for backwards-compatible one-shot runs.
- **PyInstaller build harness** (`build/`) — spec file + PowerShell driver to produce a single
  `dist/bpi-launcher.exe` on a Windows host.
- **Claude SKILL.md** at the project root — frontmatter + Claude-facing manual. The project is now both
  a Python CLI/app **and** a Claude skill.
- **Reference docs** — `references/hub-architecture.md` and `references/scoring-tables.md` extracted
  from the V1 scope for quick lookup. Original scope retained at `references/bpi-scope.md`.

### Changed

- `pyproject.toml` — version → 1.2.0; added `watchdog>=4.0` to deps; added `pyinstaller>=6.0` to `[dev]`;
  registered `bpi-launcher` script entry point.
- `.gitignore` — excludes the SQLite DB, log files, status file, real CSVs, and generated outputs.

### Unchanged

- All V1.1 scoring modules (`src/scoring/*`) — same code, now invoked over the SQLite-hydrated dataframe
  rather than directly off the CSV.
- `src/sources/rpdata_csv.py` — same loader, used by both `bpi run` and `bpi ingest`.
- `src/output/{excel,html_report}.py` — same rendering, called by both the one-shot pipeline and the
  Hub's dashboard regen.
- `config/scoring-weights.yaml` — same tunable patterns, applied during recompute.

## V1.1 — 23-05-2026 21:38

Tested on 7,408 records across Currimundi + Aroona + Wurtulla. Findings:
- 53 HIGH Seller Leads, 106 HIGH Rental Leads, 183 multi-property owners,
  21 with 3+ properties, 1 portfolio investor (4+), 43 cross-suburb owners

### Fixes

- **CSV header auto-detection** (`src/sources/rpdata_csv.py`)
  - Handles RP Data exports that include a "Search String" metadata preamble
    (Wurtulla format) as well as direct-header exports (Currimundi format).
  - Loader now scans the first 10 lines and finds the row containing
    `Street Address` + `Owner 1 Name` to use as the header.
- **Sale Price parsing** (`src/sources/rpdata_csv.py`)
  - Handles "Not Disclosed" and other non-numeric sale price values
    without erroring. Uses `pd.to_numeric(..., errors='coerce')`.
- **Unknown owner aggregation** (`src/scoring/portfolio.py`)
  - Owners with names `-`, `UNKNOWN`, blank, or `NAN` are now excluded
    from portfolio counting (previously inflated counts by grouping all
    unknowns under one row).
- **Non-saleable patterns** (`config/scoring-weights.yaml`)
  - Added: OZCARE, BLUECARE, ANGLICARE, UNITINGCARE, MERCY AGED,
    SOUTHERN CROSS CARE, REGIS AGED CARE, BUPA AGED, OPAL AGED, RSL CARE,
    MASONIC CARE, TRICARE, ESTIA HEALTH (aged care)
  - Added: COAST2BAY HOUSING, COMMUNITY HOUSING, HOUSING GROUP LIMITED,
    HOUSING TRUST (community housing)
  - Added: CHURCH OF, ARCHDIOCESE OF, DIOCESE OF, TRUSTEES OF THE,
    SALVATION ARMY, ANGLICAN CHURCH, CATHOLIC CHURCH (religious orgs)

### Open items for V1.3 (refinements identified during three-suburb testing)

- Add `UNITING CHURCH IN AUSTRALIA` pattern (saw at 1 Lake Kawana
  Boulevard, Wurtulla — religious trust slipping through current patterns).
- Add `NORTHERN SEQ DISTRIBUTOR-RETAILER AUTHORITY` (utility infrastructure
  holder, currently misclassified as Individual).
- Consider treatment of `PUBLIC TRUSTEE OF QUEENSLAND` — currently scored
  as legitimate Seller Lead (correct: these are deceased estate properties
  with a duty to liquidate; keep but flag context in Recommended Action).
- Consider `CLUB` and `COMMUNITY CLUB` patterns — boundary case, leaving
  unfiltered for now (Mitch judgment call).

## V1.0 — 23-05-2026 20:38

Initial build. CSV ingest, current owner derivation, portfolio counting,
Seller Lead + Rental Lead + Combined Score, branded Excel output, HTML
report, CLI. Tested on 3,257-row Currimundi CSV.
