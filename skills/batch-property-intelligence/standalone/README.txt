BATCH INTELLIGENCE HUB — Browser Edition  (V4.7)
Elite Lifestyle Properties

V4.7 — Inspections stamped against the person; scaled warmth.

THE RULE: the more inspections a person attends, the warmer
they are. And if they inspected a listing WE are selling while
owning a property on the Sunshine Coast, they may be a seller.

- Every person now carries a purple "🏠 N×" attendance pill and
  an "Insp #" column in Holding AND Warm Sellers (both sortable
  high→low alongside Enq #).
- Holding default order is now Enq # → Insp # → most recent, so
  the most-engaged unmatched people surface first; their
  attendance count rides along into the Holding CSV and the
  Outreach List (new "Insp #" column, used as a sort tiebreak).
- The inspection score boost now SCALES with attendance, same
  tiering as repeat enquirers: base +3 for any attendance, +1
  more at 3-5 opens, +2 more at 6+, capped at 20. Recommended
  Action reads "inspected our listing N× & owns SC — potential
  seller."
- The Top Inspectors leaderboard labels every attendee-owner
  match as "POTENTIAL SELLER", and a new dashboard stat card
  ("🏠 Inspector sellers") counts them at a glance.
- Person-matching is token-based, so "John Smith" on the report
  matches "SMITH JOHN" on an enquiry.

V4.6 — Inspections PDF import + Top Inspectors leaderboard.

IMPORT INSPECTIONS PDF. New "Import Inspections PDF…" button
takes the CRM's per-agent Inspections Report PDF straight in —
no copy/paste needed. The Hub reads the PDF entirely in the
browser (no upload, no dependency), reconstructs the table
(client, phone, date, property, interest — wrapped names and
two-line addresses handled), groups rows into open-home events,
and runs every attendee through the owner-matching engine.
Tested against real reports: 306/306 and 98/98 rows captured.
Re-importing the same file replaces its prior events rather
than duplicating. The agent's name is captured per event.

TOP INSPECTORS. The Inspections tab now opens with a sortable
leaderboard of every attendee across all saved inspections:
Insp # (how many opens they've attended), properties visited,
last inspection date, phone, and whether they matched an SC
owner (with owned address + score). Click any header to sort
high→low / low→high — repeat inspectors are the hot prospects.
A 🏠 N× pill marks anyone with 2+ attendances. Event cards
below collapse to one line each (tap to expand).

SORTING. Warm Sellers gains a sortable "Insp #" column next to
"Enq #", so enquiry count and inspection count both sort
high-to-low with one click. An enquirer who also owns SC
property AND attends opens is about the strongest signal there
is — these now bubble straight to the top.

The complete workbook gains a "Top Inspectors" sheet and the
Inspections sheet now carries Phone + Agent (workbook now 13
tabs). Owner-level Insp # is exported on Warm Sellers / High
Priority / All Properties / Under Management.

V4.5 — Enquiry column on every tab + matching workbook tabs.
An enquirer who also owns ≥1 SC property is nearly the best
lead we can have, so every property tab now carries:
  · Enq # (count of enquiries from the matched owner)
  · Enquirer (name, with the 🔁 N× pill when ≥2)
  · Status pill (★ WARM / 🏠 open home / UM)
…and the default order on every property tab is now
WARM-FIRST, then most-enquiries, then score. Quick scroll to
the top of any tab and the strongest leads are already there.

Owner-level signals propagate too: if the owner enquired on a
different property they hold, every parcel of theirs now shows
"★ owner warm" with the same enquirer name + date, so cross-
suburb portfolios light up automatically on every tab.

Workbook (Master Dashboard XLSX) is rebuilt to carry the same
data through every sheet:
  · Under Management — gains Warm Seller, Enq #, Enquirer,
    Enquiry Date, Buyer Bracket, Active Buyer, Owner Warm,
    Owner Enquirer, Owner Enq #, Attended Open Home.
  · High Priority / Seller Leads / All Properties / Filtered —
    same enquiry-signal columns added to EXPORT_COLS.
  · Portfolios / Rentals matrices — first three columns are
    now Enq #, Warm Enquirer, Enquiry Date so you can sort by
    them in Excel.
  · Warm Sellers — gains Attended Open Home flag.
  · New "Inspections" sheet — flat list of attendee→owner
    match rows from every saved open-home inspection.
Workbook is now 12 tabs.

V4.4 — Three additions:

1. INSPECTION SCREENSHOT MATCH. New "Match Inspection List…"
   button in the import toolbar. Tap it at an open home, pick the
   screenshot from your phone of the agent-list software, long-
   press the names in the preview (iOS Live Text) → Copy → paste
   into the textarea, hit "Match & save". Every line runs
   through the existing owner-matching engine. Strong matches
   (first-name + surname agreement) earn a +3 score boost
   ("attended open home") on every parcel that owner holds in
   your database — a confirmed in-person attendee is a stronger
   signal than a remote enquirer. History lives in a new
   "Inspections" tab next to Warm Sellers; each event is
   expandable with attendee→owner rows.

2. PASSCODE GATE. The app now boots behind a 4-digit code
   (default 4551). The hash is in localStorage; entering the
   code unlocks the session (kept in sessionStorage so a reload
   in the same tab stays unlocked). Change the code in Scoring
   Settings → Passcode. A "🔒 Lock now" button on the memory
   toolbar re-locks immediately. SOFT GATE ONLY — this is a
   single-file HTML, so anyone willing to open DevTools can
   bypass it. It keeps casual eyes off the data; it does NOT
   encrypt anything. If you need real protection ask for AES-GCM
   encryption of the memory file as a follow-up.

3. RULE TWEAKS (configurable in settings):
   - Lease-expiry boost: a managed property whose tenancy ends
     in ≤90 days gives the owner +1 (vendors often think about
     selling when the lease is up). Set days to 0 to disable.
   - Active-buyer × warm-seller dual boost: warm sellers whose
     enquiry is flagged as an Active Buyer get +1 — they're
     actively shopping for an upgrade.
   - Inspection boost (above): +3 stackable.
   All three stack with warm (+2), managed (+5), and repeat-
   enquirer (+1/+2), still capped at score 20.

Memory-file payload version bumps to v6 (with new "inspections"
key). Loading an older v5 file works — inspections default to
empty.

V4.3 — Holding and Warm Sellers column headers are now click-to-
sort (click again to reverse). Tap "Enq #" to put your hottest
repeat enquirers up top, or any other column. Active sort key
is highlighted gold with an arrow.

V4.2 — Summary tab gains an Enquiry Momentum bar chart showing
the last 18 months of enquiry volume (inline SVG, no deps).

V4.1 — Each owner row carries a clickable "✓ N" outreach
counter. Click to log one contact, shift-click to reset; tick
multiple rows and use the sticky "Mark contacted" bar to bump
many at once. Persists per-owner in the OneDrive memory file.
"Contacted #" + "Last Contacted" added to CSV / workbook
exports.

V4.0 — Two new things in the export bar:
- "Buyer $$$" dropdown (Any / <$500k / $500k–$1M / $1M–$2M /
  $2M–$5M / $5M+) — narrows the Holding, Warm Sellers and the
  workbook to one buyer price bracket, in addition to the
  existing suburb filter.
- "Outreach List (CSV)" button — combines warm sellers + active
  enquirers (Holding) into ONE file, with DNC rows removed
  automatically. Sorted by score then enquiry count, with
  Phone, Email, Buyer $$$, OUR PM, INV and recommended-action
  notes. Ready to hand to an agent. Also appears in the
  complete workbook as a new "Outreach (DNC excluded)" tab
  (workbook now 11 tabs).

V3.9 — Repeat enquirers now move the Combined Score: a warm
seller whose matched enquirer has 3-5 enquiries gets +1, ≥6
gets +2 (stackable with warm +2 and managed +5, capped at 20).
The Recommended Action also notes "— repeat enquirer (N×)."
Warm Sellers re-sorts within each score by enquiry count.

V3.8 — Holding now opens sorted by enquiry count (highest first)
so the most-engaged people sit at the top, plus dashboard stat
cards for "Unique enquirers" and "🔁 Repeat enquirers (≥2)".

V3.7 — Each enquirer carries an "Enq #" count showing how many
separate enquiries they've made across all loaded files. Anyone
with ≥2 enquiries gets an orange "🔁 N×" badge next to their
name in Holding and Warm Sellers. The count is a sortable
column in both views and is included in CSV / workbook exports.

V3.6 — DNC enquirers (do-not-contact / do-not-call / do-not-email
flagged in the source CSV) are now shown with RED text and a
DNC badge on every Holding / Warm Sellers row, so you can't
accidentally outreach them. Also: when an enquiry's "Property
Enquired On" address matches a property in your Managed Properties
list, the row shows a blue "OUR PM · Residential" badge — a strong
cross-signal that the enquirer is shopping for one of our managed
rentals.

V3.5 — enquiry import gains "Buyer $$$" (price of the property
they enquired on, looked up from RP Data sales) and a "Potential
Investor" flag (notes mention "invest"). Handles the LockedOn
report_84.csv format (hyphenated headers, ISO dates) with no
column-mapping prompt. Also reads active-buyer and the three
do-not-contact/call/email flags. Holding tab columns are now
focused: Name, Enquiry Date, Phone, Email, Active Buyer,
Property Enquired On, Buyer $$$, Buyer Bracket, Potential
Investor, Lead Source, Source File. Warm Sellers picks up the
same enquiry-side fields next to the owned-property data.

V3.4 is mobile-friendly. Open bpi-hub.html on an iPhone (use
Safari, then "Add to Home Screen" if you want it as an icon).
The tab bar swipes left/right, stat cards reflow to 2-per-row,
modals stack vertically, and the search box fills the screen.
Recommended-action / suggestion copy is also shorter so rows
stay compact on a small screen.

V3.2 fixes a counting bug where letter-suffixed street numbers
(e.g. 19A Aroona Av, Unit 10N / 143 Lowanna Dr, 2A Hill St) used to
fall through to a garbage postcode-only key, which would then
falsely match every other letter-suffixed RP Data parcel in the
same postcode. Re-uploading an Owner export now also cleanly
replaces that file's prior entries instead of inflating counts.
The Scoring settings panel adds a "Clear entire managed list"
button as an escape hatch and shows the current stored counts.

================================================================
WHAT'S IN THIS FOLDER
================================================================

  bpi-hub.html        The app. Double-click to open in Edge or Chrome.
  bpi-database.json   Your memory file. The app saves EVERYTHING here —
                      sales, enquiries, your scoring settings, and your
                      Review-Matches approvals — so it all follows the
                      OneDrive file across machines.
  README.txt          This file.

Keep all three together in the one folder (e.g. on OneDrive).
The .html is self-contained — it needs no internet and nothing
gets uploaded anywhere. All processing happens on your machine.

================================================================
FIRST-TIME SETUP (once)
================================================================

  1. Put this whole folder where you want it, e.g.
     OneDrive\...\09_Local-Tools\Skills\batch-intelligence\

  2. Double-click  bpi-hub.html  (opens in Edge/Chrome).

  3. Click  "Link OneDrive memory file..."
     In the dialog, select the bpi-database.json that's already
     in this folder (or save a new one here).

  4. The status chip turns gold:
     "Memory: bpi-database.json (auto-saving)".

Done. From now on everything you do is saved to that file.

================================================================
DAILY USE
================================================================

  - Drag an RP Data CSV export onto the top drop zone (or click
    "Pick RP Data CSV..."). The dashboard appears instantly.

  - Drop more CSVs (other suburbs, owner-search exports). They
    ADD to what's already there — owners who hold property across
    several suburbs show up in the Portfolios tab automatically.

  - Drop the same file twice? No problem — it de-duplicates.

  - Tabs: Summary, High Priority, Warm Sellers,
    Under Management, Holding (Pending RP Data),
    Portfolios, Rentals, All Properties, Filtered Out.

================================================================
UNDER MANAGEMENT  (Properties we already manage)
================================================================

  - Drop your Owner Export (a CSV from the property-management
    console, with Address + Ownership columns) via the
    "Pick Managed Properties CSV..." button.

  - On upload a small dialog asks which portfolio it represents
    (Residential / Residential 1 / Residential 2). The default
    is picked in this order:
      1. Property Manager → Portfolio mapping you've saved
         (e.g. "Cheyenne O'Leary" → Residential).
      2. Filename keywords (e.g. residential_1 → Residential 1).
      3. Plain "Residential".
    Override the dropdown if you want, and your choice is
    remembered for that Property Manager next time.
    If the CSV itself has a Portfolio column, that value wins
    per row.

  - To VIEW or EDIT the PM → Portfolio mappings later, open
    "Scoring settings" and scroll to "Property Manager →
    Portfolio Mapping". Change any row's dropdown and click
    "Save PM mappings". Saved into your OneDrive memory file.

  - The tool builds two indexes from the file:
      • PER-OWNER  — every owner name is flagged "under
        management". Wherever that owner appears across the
        dashboard (Warm Sellers, leads tables, Portfolios,
        search results) they show a blue UM badge so you can
        instantly see we already have the relationship.
      • PER-PROPERTY  — addresses are normalised (Av → Avenue,
        units like "12/44 Alexandra Pde" handled) and matched
        against the RP Data parcels. The Under Management tab
        lists every parcel match with portfolio, property
        manager, current tenancy and rent.

  - Combined Score gets a +5 boost on every parcel under
    management (stackable with the warm-seller +2).

  - Re-uploads MERGE; entries are updated but never wiped, so
    your manual postal/notes and prior portfolio assignments
    survive future Owner exports.

================================================================
SCORE TIERS  (1–20 with HOT / FLAMING HOT)
================================================================

  Combined Score now runs 1–20 (was 1–10). Two new tiers:

      🔥 HOT          score > 10
      🔥🔥 FLAMING HOT  score > 15

  Boosts (stackable, capped at 20):
      Warm seller (LockedOn match + own SC property)  +2
      Under our management                            +5

  A warm seller you also manage on a max-base (10) parcel
  reaches 17 — FLAMING HOT — the strongest possible signal.

================================================================
ENQUIRY DATA  (LockedOn  OR  RP Data enquiries)
================================================================

  - Drop an enquiry export onto the SECOND drop zone (or click
    "Pick LockedOn CSV..."). It accepts BOTH LockedOn exports and
    RP Data enquiry exports — columns are auto-detected.

  - WARM SELLER rule: an enquirer who is in your database AND
    owns a CURRENT Sunshine Coast property is flagged a warm
    seller — highlighted with a gold star and given +2 points.
    They appear in the Warm Sellers tab and are starred wherever
    they show up. (Recency window tunable in Scoring settings.)

  - Matching is STRICT: a name is auto-flagged warm only when the
    first name AND surname agree (e.g. "Darlene Burnett" =
    "Darlene Denise Burnett"). This avoids false hits from common
    names.

  - REVIEW MATCHES tab: when a match is uncertain — same surname
    but a different first name, or one enquirer hitting several
    owners (e.g. "Peter James" matching three different owners) —
    it's listed here instead of auto-flagged. Click "✓ Warm
    seller" to confirm (that owner then gets the star + 2 points)
    or "✕ Not a match" to dismiss. Your decisions are remembered.

  - HOLDING (Pending RP Data): an enquirer who is NOT yet
    confirmed as a current SC owner lands in the Holding tab.
    These are people to look up: pull their RP Data, drop the
    suburb export in, and any who own on the Coast move to Warm
    Sellers automatically.

  - COLUMN MAPPING APPROVAL: if the app isn't fully sure which
    columns are which (e.g. an RP Data export with "user name"),
    it shows a mapping dialog before importing. Anything matched
    loosely is flagged "(check)" — confirm or correct the dropdowns,
    then click "Import with these columns". Clean LockedOn exports
    import straight through with no prompt.

================================================================
SEARCH
================================================================

  - The search box at the top of the dashboard finds any
    address, owner, or enquirer name. Type 2+ characters; warm
    sellers among the matches are shown first.
    Clear it (or click any tab) to return to the dashboard.

================================================================
EXPORTS
================================================================

  - "Complete workbook (Excel, all tabs)" — one .xlsx with nine
    tabs: Summary, Warm Sellers, High Priority, Seller Leads,
    Rentals, Portfolios, All Properties, Holding (Pending RP Data),
    Filtered Out. Bold headers, frozen top row, auto-filter on
    every column.

  - Targeted CSV buttons: Warm Sellers, Holding (Pending RP Data),
    Seller Leads, Rentals, Portfolios, High Priority, All Properties.

  - SUBURB FILTER: the "Suburb" dropdown in the Exports bar limits
    EVERY export (warm sellers, all the leads lists, rentals,
    portfolios, holding, and the complete workbook) to a single
    suburb — handy for handing an agent just their patch. Leave it
    on "All suburbs" for the full set. The chosen suburb is added
    to the file name.

================================================================
POSTAL ADDRESSES / NOTES  (maintaining the master)
================================================================

  RP Data doesn't export a postal/mailing address, so that column
  comes out blank. You can fill it in yourself and the tool will
  KEEP it — uploads never overwrite your entries.

  1. Export any list that has an Owner + Postal Address column
     (e.g. All Properties, Warm Sellers) — or the complete
     workbook.
  2. In Excel, type the owner's mailing address into the Postal
     Address column (and anything you like into Notes).
  3. Back in the app, click "Update postal/notes from sheet..."
     and pick that file.

  The tool reads Owner + Postal Address (+ Notes), stores them
  PER OWNER, and applies them to every one of that owner's
  properties. Only non-blank cells are taken, so it never wipes
  what you've entered. Everything is saved into the OneDrive
  memory file, so your postal addresses follow you and survive
  future RP Data / enquiry uploads. Re-export any time for an
  up-to-date master.

  - Portfolios tab/export lists each of an owner's Sunshine
    Coast holdings in its OWN column (SC Property 1, SC Property
    2, ...). It also has a Postal Address column — populated if
    your RP Data export includes a postal/mailing address
    column, otherwise left blank to fill in later.

  - Rentals tab/export is rolled up per landlord: Top Score
    (highest first), Owner, Rentals count, a Suburbs column, and
    each rental property in its OWN column (Rental Property 1,
    2, ...).

  - Every property list/export also carries a Suburb column next
    to the address, so you can sort by suburb in Excel.

================================================================
EVERY TIME YOU REOPEN IT
================================================================

When you open the .html in a fresh browser session you'll see:

     "Memory: ... click Reconnect"

Click  "Reconnect memory file"  once. (Browsers require a click
to re-grant file access — it's a security rule, not a fault.)
Your data loads and auto-saving resumes. Same data, one click.

================================================================
USING IT ON ANOTHER COMPUTER
================================================================

Because the folder is on OneDrive, open bpi-hub.html on the other
PC and either click "Reconnect" or "Link OneDrive memory file..."
and point at the same bpi-database.json. Your whole database is
there.

Don't run it and ingest on two machines at the SAME time — OneDrive
would treat that as a sync conflict. One machine at a time is fine.

================================================================
IF YOUR BROWSER DOESN'T SUPPORT LINKING (Firefox / Safari)
================================================================

You'll only see "Save a copy..." and "Load a copy..." buttons.
Use Edge or Chrome for the auto-saving memory file. With Firefox/
Safari you can still work — just Save a copy to keep your data and
Load a copy to bring it back.

================================================================
TUNING THE SCORING
================================================================

Open the "Scoring settings" panel to adjust postcodes, the
long-held / recent-purchase thresholds, and the entity /
non-saleable name patterns. Click "Apply & recompute".
Settings are saved in the browser.
