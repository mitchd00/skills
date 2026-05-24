# BPI Scoring Tables — Quick Reference

Lifted from §7 of `bpi-scope.md`. Source of truth for the scoring logic. Patterns and thresholds are
tunable in `config/scoring-weights.yaml`.

## Entity vs Individual classification

`Owner Classification = "Entity"` if Owner 1 Name contains any of (case-insensitive):

`PTY LTD`, `PTY. LTD`, `LIMITED`, ` LTD`, `TRUST`, `SUPER`, `SUPERANNUATION`, `SMSF`, `NOMINEES`,
`HOLDINGS`, `INVESTMENTS`, `PROPERTIES`, ` GROUP`, ` CO.`, ` & CO`, `PARTNERSHIP`, `CORPORATION`, `ENTERPRISES`.

Otherwise `"Individual"`. `-`, blank, `NAN`, `UNKNOWN` → `"Unknown"`.

## Non-saleable filter

Filters owners + land uses that aren't valid lead targets. Routes to the "Filtered Out" sheet.

**Owner patterns** (any of, case-insensitive substring match):

Government / utilities: `RESERVE FOR`, `SUNSHINE COAST REGIONAL COUNCIL`, `SUNSHINE COAST COUNCIL`,
`STATE OF QUEENSLAND`, `DEPARTMENT OF`, `COMMONWEALTH OF AUSTRALIA`, `CROWN LAND`, `QUEENSLAND RAIL`,
`ENERGEX`, `TELSTRA CORPORATION`, `AUSTRALIA POST`.

Aged care: `OZCARE`, `BLUECARE`, `ANGLICARE`, `UNITINGCARE`, `MERCY AGED`, `SOUTHERN CROSS CARE`,
`REGIS AGED CARE`, `BUPA AGED`, `OPAL AGED`, `RSL CARE`, `MASONIC CARE`, `TRICARE`, `ESTIA HEALTH`.

Community housing: `COAST2BAY HOUSING`, `COMMUNITY HOUSING`, `HOUSING GROUP LIMITED`, `HOUSING TRUST`.

Religious: `CHURCH OF`, `ARCHDIOCESE OF`, `DIOCESE OF`, `TRUSTEES OF THE`, `SALVATION ARMY`,
`ANGLICAN CHURCH`, `CATHOLIC CHURCH`.

**Land Use patterns** (any of, case-insensitive substring match):

`Reserves`, `Recreational`, `Public Buildings`, `Educational - Govt`, `Roads`, `Drainage`, `Cemetery`.

## Seller Lead matrix

| Owner SC Property Count | Entity? | Other signals | Seller Lead |
|---|---|---|---|
| ≥ 4 | any | any | **HIGH** + portfolio investor flag |
| 3 | any | any | **HIGH** |
| 2 | any | any | **MEDIUM** |
| 1 | Entity | any | **MEDIUM** (corporate holding structure) |
| 1 | Individual | Long-held (≥ `long_held_years`) + Owner Type = Rented | **MEDIUM** |
| 1 | Individual | Long-held (≥ `long_held_years`), owner-occupier | **LOW** |
| 1 | Individual | Recent purchase (< `recent_purchase_years`) | **NO** |
| 1 | Individual | Mid-range hold | **LOW** |
| Unknown / non-saleable | — | — | **NO** (filtered) |

Defaults: `long_held_years = 15`, `recent_purchase_years = 5`.

## Rental Lead matrix

| Owner Type | Owner SC Rental Count | Rental Lead |
|---|---|---|
| `Rented` | ≥ 2 | **HIGH** — multi-property landlord, full PM pitch |
| `Rented` | 1 | **MEDIUM** — single-property landlord, PM pitch valid |
| Unknown / blank | ≥ 1 | **LOW** — investor pattern, confirm before pitching |
| `Owner Occupied` | — | **NO** |
| Government / Reserve / non-saleable | — | **NO** (filtered) |

## Combined Lead Score (1–10) + Recommended Action

| Seller Lead | Rental Lead | Score | Recommended Action |
|---|---|---|---|
| HIGH | HIGH | 10 | Seller + PM combined pitch — portfolio investor with rentals. Approach with portfolio review framing. |
| HIGH | MEDIUM | 9 | Seller approach + PM upsell |
| HIGH | LOW | 8 | Seller approach — multi-property owner, possible rental in portfolio |
| HIGH | NO | 8 | Seller approach — multi-property owner, mostly owner-occupied |
| MEDIUM | HIGH | 7 | PM pitch first, seller conversation second |
| MEDIUM | MEDIUM | 6 | PM pitch, mention sales side |
| MEDIUM | LOW | 5 | Long nurture — DNA Plan #1, possible PM |
| MEDIUM | NO | 5 | Long nurture — DNA Plan #1 |
| LOW | HIGH | 5 | PM pitch only |
| LOW | MEDIUM | 4 | PM pitch only |
| LOW | LOW | 3 | Long nurture |
| LOW | NO | 3 | Long nurture |
| NO | HIGH | 4 | PM pitch only — non-saleable but rental opportunity |
| NO | MEDIUM | 3 | PM pitch only |
| NO | LOW | 2 | Cache for future |
| NO | NO | 1 | Skip |

## SC postcode coverage (for portfolio counting)

Defaults in `config/scoring-weights.yaml`:

- 4551 (Caloundra catchment) — Tier 1 = Pelican Waters canal, Kings Beach, Moffat Beach, Shelly Beach
- 4575 (Kawana/Buddina) — Tier 1 = Minyama canal, Parrearra Headland, Buddina absolute
- 4556 (Buderim) — borderline, included
- 4557 (Mooloolaba), 4558 (Maroochydore), 4573 (Coolum), 4566 (Noosa Heads)
