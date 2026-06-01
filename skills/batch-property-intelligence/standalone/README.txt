BATCH INTELLIGENCE HUB — Browser Edition  (V3.4)
Elite Lifestyle Properties

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
