# Batch Property Intelligence — V1 Scope

**Project:** `batch-property-intelligence`
**Version:** V1
**Created:** 23-05-2026 20:38
**Owner:** Mitchell Dunne — Elite Lifestyle Properties
**Status:** Draft
**Destination:** `Projects\ELITE-Project-System\10_Code-Projects\batch-property-intelligence\`

---

## 1. Purpose

A batch property research tool that processes up to 500 RP Data records at once, enriches them across multiple free public data sources, applies Seller Lead and Rental Lead scoring, and outputs a branded Excel + HTML report ready for actioning. Feeds the `property-intelligence-dossier` skill for deep workups on the top scorers.

This is the **volume layer** of the ELP research stack. The dossier skill is the depth layer.

---

## 2. The architectural funnel

Three-stage pipeline. V1 implements Stage 1 only; later phases add Stage 2 and 3.

| Stage | Properties | Sources | Cost per run | Output |
|---|---|---|---|---|
| **1. Bulk enrichment + scoring** | Up to 500 | RP Data CSV (your manual export) + ABN Lookup + ACNC + ASIC free + QLD Globe + SCC open data + Google Custom Search + Google Maps Static | ~$15–$20 (or $0 if Google APIs deferred) | Scored Excel ranking all 500 + HTML scan report |
| **2. Filtered deep search** | Top ~50 (V2) | ASIC paid extracts, news archives, electoral roll, LinkedIn check | ~$1,100 (50 × $22 ASIC) | Enriched JSON per property |
| **3. Dossier candidates** | Top ~10–15 (V2.1) | Hand-off to `property-intelligence-dossier` skill | ~$330 (10 × $33 titles) | Full Word + PDF dossier |

---

## 3. V1 scope

In scope for V1:

- Single-CSV input (RP Data export, one suburb or postcode at a time)
- Multi-CSV input optional (combine 4551 + 4575 exports for cross-suburb portfolio counting)
- Current-owner derivation per parcel (latest sale = current owner)
- Owner portfolio counting (count distinct properties per owner across the input)
- Rental status from RP Data `Owner Type` field
- Absentee owner flag (requires postal address in CSV — flag if missing)
- Entity vs individual owner classification
- Government / reserve / non-saleable filtering
- Seller Lead scoring (HIGH / MEDIUM / LOW / NO)
- Rental Lead scoring (HIGH / MEDIUM / LOW / NO)
- Combined Lead Score (1–10)
- Recommended Action
- Branded Excel output with conditional formatting
- HTML summary report

Out of scope for V1 (deferred to later phases):

- ASIC API integration (paid extracts) — V2
- ACNC, ABN Lookup integration — V1.1 (cheap, fast)
- QLD Globe + SCC open data — V1.1
- Google Custom Search news lookup — V1.1
- Aerial imagery via Google Static Maps — V1.2
- LockedOn cross-check via MCP — V1.2
- Direct dossier handoff — V2.1
- Web UI — not planned (CLI only)
- Real-time RP Data API integration — never (T&Cs, use CSV path)

---

## 4. Folder structure

```
10_Code-Projects\batch-property-intelligence\
├── README.md
├── pyproject.toml
├── .env.example                       # template for optional API keys
├── docs/
│   └── BPI_Scope_V1_23-05-2026_2038.md   # this document
├── config/
│   └── scoring-weights.yaml
├── src/
│   ├── __init__.py
│   ├── main.py                        # CLI entry point
│   ├── pipeline.py                    # orchestrator
│   ├── sources/
│   │   ├── __init__.py
│   │   └── rpdata_csv.py              # RP Data CSV ingest + normalisation
│   ├── scoring/
│   │   ├── __init__.py
│   │   ├── current_owner.py           # derive current owner per parcel
│   │   ├── portfolio.py               # owner portfolio counting
│   │   ├── seller_lead.py             # Seller Lead scoring
│   │   ├── rental_lead.py             # Rental Lead scoring
│   │   └── combined.py                # combined score + recommended action
│   ├── output/
│   │   ├── __init__.py
│   │   ├── excel.py                   # branded Excel output
│   │   └── html_report.py             # HTML scan report
│   └── cache/
│       ├── __init__.py
│       └── db.py                      # SQLite for resume state (V1.1+)
├── inputs/                            # drop your CSV exports here
│   └── .gitkeep
├── outputs/                           # tool writes results here
│   └── .gitkeep
├── tests/
│   ├── __init__.py
│   └── test_scoring.py                # unit tests for scoring logic
└── Archive/                           # per ELP archive rule
```

---

## 5. Input format

V1 accepts the standard RP Data CSV export. From inspection of the Currimundi May 2026 sample, the columns are:

```
Street Address, Suburb, State, Postcode, Council Area, Property Type,
Bed, Bath, Car, Land Size (m²), Floor Size (m²), Year Built,
Sale Price, Sale Date, Settlement Date, Sale Type, Agency, Agent,
Land Use, Development Zone, Parcel Details,
Owner 1 Name, Owner 2 Name, Owner 3 Name, Owner Type,
Vendor 1 Name, Vendor 2 Name, Vendor 3 Name, Open in RPData
```

Critical notes from sample inspection:

- The CSV is **historical sales**, not current ownership. Each row is a sale event.
- Multiple sales per parcel exist. Current owner = owner from the **most recent sale per parcel**.
- `Owner Type` carries the rental status: `Owner Occupied`, `Rented`, `Government Owned - Other`, `Government Owned - Rented`, or `-` (unknown).
- Some parcels are not saleable: `RESERVE FOR PARK`, `RESERVE FOR BUFFER ZONE`, `SUNSHINE COAST REGIONAL COUNCIL`, state government departments. These are filtered out of the lead list.
- BOM-encoded UTF-8 — read with `encoding='utf-8-sig'`.
- Sale Date format: `09 Nov 2000` (day-month-year, three-letter month).

For multi-CSV cross-suburb portfolio counting, the user provides one CSV per suburb/postcode and the tool concatenates before deriving current owners.

---

## 6. Output format

### Primary output: Excel workbook

Filename: `<Region>_BatchIntelligence_V<N>_<DD-MM-YYYY_HHMM>.xlsx`

Sheets:

1. **Summary** — top-line stats, distribution of lead grades, top 20 scorers
2. **All Properties** — every row from the input with all enrichment columns appended
3. **High Priority** — filtered to HIGH Seller Lead OR HIGH Rental Lead, sorted by Combined Score desc
4. **Portfolios** — pivot of owners with 2+ properties, sorted by property count desc
5. **Rentals** — properties classified as rentals, sorted for PM pitch priority
6. **Filtered Out** — government, reserves, council-owned (transparency: shown what was excluded)

Each sheet branded with ELP colours (Elite Black, Warm White, Muted Gold). Header rows frozen. Auto-filter on every column. Conditional formatting highlights HIGH leads in gold.

### Secondary output: HTML scan report

Filename: `<Region>_BatchIntelligence_Report_V<N>_<DD-MM-YYYY_HHMM>.html`

Single-page summary readable in 60 seconds:

- Headline counts (total, high-priority, rentals, portfolios)
- Top 10 scorers as cards
- Distribution charts (lead grade, owner type, property type)
- Recommended next actions

---

## 7. Scoring logic (V1)

### 7.1 Current owner derivation

For each parcel, take the row with the latest `Sale Date`. That row's `Owner 1 Name` is the current owner. Carry forward `Owner Type`, `Owner 2 Name`, `Owner 3 Name`.

If a parcel has no sales recorded but appears in the CSV, treat owner as `Unknown` and skip lead scoring.

### 7.2 Non-saleable filtering

Filter out and route to "Filtered Out" sheet:

- Owner name matches: `RESERVE FOR`, `SUNSHINE COAST REGIONAL COUNCIL`, `STATE OF QUEENSLAND`, `DEPARTMENT OF`, `COMMONWEALTH OF AUSTRALIA`, `BODY CORPORATE FOR` (the BC entity itself, not the underlying lots)
- Land Use matches: `Reserves`, `Recreational`, `Public Buildings`
- Property Type = `Land: Res Development` where owner is corporate developer (flag separately)

### 7.3 Entity vs individual classification

Owner is classified `Entity` if name contains any of:
- `PTY LTD`, `LIMITED`, `LTD`, `TRUST`, `SUPER`, `SUPERANNUATION`, `SMSF`, `NOMINEES`, `HOLDINGS`, `INVESTMENTS`, `PROPERTIES`, `GROUP`, `CO.`, `& CO`, `PARTNERSHIP`

Otherwise `Individual`.

Joint owners (Owner 2/3 names present) flagged separately.

### 7.4 Owner portfolio counting

Group by `Owner 1 Name` (case-insensitive, whitespace-normalised). For each owner, count distinct parcels. This is the `Owner SC Property Count` in the output.

Note: V1 counts within the input CSV only. For full SC portfolio counting (across 4551 + 4575), provide multiple CSVs or wait for V1.1 which adds RP Data Owner Search API integration.

### 7.5 Rental detection

Use `Owner Type` field directly:

| Owner Type value | Maps to | Confidence |
|---|---|---|
| `Rented` | Rental = Y | HIGH (RP Data confirms tenancy) |
| `Government Owned - Rented` | Rental = Y (filtered out as non-saleable) | HIGH |
| `Owner Occupied` | Rental = N | HIGH (owner-occupier confirmed) |
| `-` or blank | Rental = Unknown | LOW |

V1.1 adds REA/Domain rental history scraping as fallback for `Unknown` rows.

### 7.6 Seller Lead scoring

| Owner SC Property Count | Entity? | Other signals | Seller Lead |
|---|---|---|---|
| ≥ 4 | any | any | **HIGH** + portfolio investor flag |
| 3 | any | any | **HIGH** |
| 2 | any | any | **MEDIUM** |
| 1 | Entity | any | **MEDIUM** (corporate owner of single property — often a holding structure) |
| 1 | Individual | Long-held (>15 years) + absentee | **MEDIUM** |
| 1 | Individual | Long-held (>15 years), owner-occupier | **LOW** |
| 1 | Individual | Recent purchase (<5 years) | **NO** |
| Unknown / non-saleable | — | — | **NO** (filtered) |

### 7.7 Rental Lead scoring

| Owner Type | Owner Property Count | Rental Lead |
|---|---|---|
| Rented (confirmed) + Owner has 2+ rentals in portfolio | — | **HIGH** (multi-property landlord, full PM pitch) |
| Rented (confirmed) | 1 | **MEDIUM** (single-property landlord, PM pitch valid) |
| Unknown + absentee owner + investor-pattern property | — | **LOW** (likely rental, confirm before pitching) |
| Owner Occupied | — | **NO** |
| Government / Reserve | — | **NO** (filtered) |

### 7.8 Combined Lead Score (1–10)

| Seller Lead | Rental Lead | Score | Recommended Action |
|---|---|---|---|
| HIGH | HIGH | 10 | **Seller + PM combined pitch** — portfolio investor with rentals. Approach with portfolio review framing. |
| HIGH | MEDIUM | 9 | **Seller approach + PM upsell** |
| HIGH | NO | 8 | **Seller approach** — multi-property owner, mostly owner-occupied |
| MEDIUM | HIGH | 7 | **PM pitch first, seller conversation second** |
| MEDIUM | MEDIUM | 6 | **PM pitch, mention sales side** |
| MEDIUM | NO | 5 | **Long nurture — DNA Plan #1** |
| LOW | HIGH | 5 | **PM pitch only** |
| LOW | MEDIUM | 4 | **PM pitch only** |
| LOW | LOW | 3 | **Long nurture** |
| NO | LOW | 2 | **Cache for future** |
| NO | NO | 1 | **Skip** |

---

## 8. Tech stack

| Component | Choice | Rationale |
|---|---|---|
| Language | Python 3.11+ | Best library ecosystem for data + Excel |
| Data | pandas | Universal, well-known, fine at this scale |
| CLI | click | Standard, clean, supports subcommands |
| Excel out | openpyxl + xlsxwriter | xlsxwriter for charts and formatting, openpyxl for editing |
| HTML out | jinja2 | Standard template engine |
| Config | PyYAML | Tunable scoring weights without code changes |
| Terminal UI | rich | Progress bars, tables, colour |
| Testing | pytest | Standard |
| Packaging | pyproject.toml + uv or pip | Modern, fast |

No credentials in code or env vars in V1. V1.1+ adds Google Custom Search API key (low sensitivity) via OS keyring or `.env`.

---

## 9. Build phases

| Phase | Scope | Time | Cost per run |
|---|---|---|---|
| **V1** | CSV ingest + portfolio counting + scoring + Excel + HTML | ~40 hours dev | Free |
| **V1.1** | Add ABN Lookup, ACNC, ASIC free, QLD Globe enrichment | ~20 hours dev | Free |
| **V1.2** | Add Google Custom Search news + aerial imagery + LockedOn MCP cross-check | ~20 hours dev | ~$15 |
| **V2** | Stage 2 — gated paid ASIC extracts + news archive deep search | ~20 hours dev | ~$1,100 when triggered |
| **V2.1** | Stage 3 — handoff to `property-intelligence-dossier` skill | ~8 hours dev | — |

V1 alone delivers the ranked Excel prospect list — the highest-value output.

---

## 10. ELP rule compliance

- **Australian spelling** throughout
- **Naming convention** — outputs follow `<Name>_V<N>_<DD-MM-YYYY_HHMM>.<ext>`
- **Archive rule** — outputs to `07_Cowork-Outputs\Batch-Intelligence-Runs\<Region-Period>\` with `Archive\` subfolder created on first run
- **VCD updates** — every run logs to the master VCD via a `--vcd-row` flag that prints the paste-ready row
- **No credentials embedded** — code-side. Optional API keys via OS keyring only.
- **Routing** — code lives in `10_Code-Projects\batch-property-intelligence\`, outputs in `07_Cowork-Outputs\Batch-Intelligence-Runs\`
- **New output subfolder needs Mitch's blessing** — `07_Cowork-Outputs\Batch-Intelligence-Runs\` is a new sibling to `CMAs\`, `Ownership-Checks\`, `Seller-Lead-Sheets\`. Same routing pattern as the Property-Intelligence-Dossiers folder added with the dossier skill.

---

## 11. Test plan

V1 ships with three tests:

1. **Unit tests** on scoring logic — known inputs produce known outputs
2. **Integration test** — process the Currimundi May 2026 CSV (3,257 rows) end-to-end, verify the Excel + HTML output
3. **Regression test** — same CSV produces deterministic output across runs (no random ordering, no time-dependent fields except the timestamp in headers)

---

## 12. VCD rows (to paste after install)

```
| batch-property-intelligence (project folder) | V1 | 23-05-2026 | 23-05-2026 | Code project | 10_Code-Projects\batch-property-intelligence\ | Batch Property Intelligence — processes up to 500 RP Data records, applies Seller Lead + Rental Lead scoring, outputs branded Excel + HTML report. V1 = CSV ingest + scoring + output only; later phases add API enrichment | Initial V1 build — funnel architecture, scoring logic locked, Currimundi sample run included | Draft | Yes |
| BPI_Scope_V1_23-05-2026_2038 | V1 | 23-05-2026 | 23-05-2026 | Markdown | 10_Code-Projects\batch-property-intelligence\docs\ | V1 scope and architecture for the batch-property-intelligence project | Initial scope document | Draft | Yes |
| Batch-Intelligence-Runs (folder) | n/a | 23-05-2026 | 23-05-2026 | Folder | 07_Cowork-Outputs\Batch-Intelligence-Runs\ | Destination subfolder for batch-property-intelligence outputs — one subfolder per region+period run | New folder created to house batch run outputs | Draft | Yes |
```

---

## 13. Open questions for Mitch

1. Confirm `07_Cowork-Outputs\Batch-Intelligence-Runs\` is the right output location, or specify alternative.
2. Confirm whether you want me to pull a second CSV (e.g. all of 4551 sales last 5 years) for cross-suburb portfolio counting in V1, or defer to V1.1.
3. Confirm whether the ELP branded Excel template lives anywhere I can lift colours/fonts directly, or if the cma-builder palette (Elite Black, Warm White, Soft Charcoal, Muted Gold) is fine to inherit.
