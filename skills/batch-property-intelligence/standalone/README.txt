BATCH PROPERTY INTELLIGENCE — Browser Edition
Elite Lifestyle Properties

================================================================
WHAT'S IN THIS FOLDER
================================================================

  bpi-hub.html        The app. Double-click to open in Edge or Chrome.
  bpi-database.json   Your memory file. The app saves everything here.
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

  - Tabs: Summary, High Priority, Portfolios, Rentals,
    Buyer Leads, All Properties, Filtered Out.

================================================================
LOCKEDON ENQUIRY DATA
================================================================

  - Drop a LockedOn export (e.g. people who enquired recently)
    onto the SECOND drop zone, or click "Pick LockedOn CSV...".

  - The app auto-detects the name / email / phone / date /
    property columns (LockedOn exports vary).

  - A contact whose NAME matches a property OWNER becomes a
    WARM SELLER signal — that owner's Combined Score is boosted
    and the row is tagged with the enquiry date. (Window is
    tunable in Scoring settings; default 6 months.)

  - A contact who does NOT match an owner becomes a BUYER LEAD,
    listed in the Buyer Leads tab with their contact details.

================================================================
SEARCH
================================================================

  - The search box at the top of the dashboard finds any
    address, owner, or contact name. Type 2+ characters; results
    show matching properties/owners AND matching contacts.
    Clear it (or click any tab) to return to the dashboard.

================================================================
EXPORTS
================================================================

  - "Complete workbook (Excel, all tabs)" — one .xlsx with eight
    tabs: Summary, High Priority, Seller Leads, Rentals,
    Portfolios, Buyer Leads, All Properties, Filtered Out.
    Bold headers, frozen top row, auto-filter on every column.

  - Targeted CSV buttons: Seller Leads, Rentals, Portfolios,
    High Priority, Buyer Leads, All Properties.

  - Portfolios tab/export lists each of an owner's Sunshine
    Coast holdings in its OWN column (SC Property 1, SC Property
    2, ...). It also has a Postal Address column — populated if
    your RP Data export includes a postal/mailing address
    column, otherwise left blank to fill in later.

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
