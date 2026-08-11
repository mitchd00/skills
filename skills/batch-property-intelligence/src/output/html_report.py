"""
HTML scan report.

Produces a single-page summary readable in 60 seconds:
  - Headline counts
  - Top 10 scorers as cards
  - Lead grade distribution
  - Recommended next actions
"""

from pathlib import Path
import pandas as pd
from jinja2 import Template


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="UTF-8">
<title>Batch Property Intelligence — {{ region }} — {{ timestamp }}</title>
<style>
  body { font-family: Arial, sans-serif; background: #F7F4EE; color: #2A2A2A; max-width: 1100px; margin: 32px auto; padding: 0 24px; }
  h1 { font-size: 24px; margin: 0 0 4px 0; color: #0A0A0A; letter-spacing: 2px; font-weight: 700; }
  .sub { color: #2A2A2A; font-size: 12px; font-style: italic; margin-bottom: 24px; border-bottom: 1px solid #B8965A; padding-bottom: 12px; }
  h2 { font-size: 13px; color: #B8965A; letter-spacing: 2px; border-bottom: 1px solid #B8965A; padding-bottom: 6px; margin: 32px 0 16px 0; }
  .stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
  .stat { background: #FFFFFF; padding: 16px; border-left: 3px solid #B8965A; }
  .stat-num { font-size: 28px; font-weight: 700; color: #0A0A0A; }
  .stat-label { font-size: 11px; color: #2A2A2A; margin-top: 4px; }
  .card-grid { display: grid; grid-template-columns: 1fr; gap: 12px; }
  .card { background: #FFFFFF; padding: 16px 20px; border-left: 3px solid #B8965A; }
  .card.score-10, .card.score-9, .card.score-8 { background: #E8DCC4; }
  .card-head { display: flex; justify-content: space-between; align-items: baseline; }
  .card-score { font-size: 22px; font-weight: 700; color: #0A0A0A; }
  .card-addr { font-size: 14px; font-weight: 600; color: #0A0A0A; }
  .card-grades { font-size: 11px; color: #B8965A; letter-spacing: 1px; }
  .card-owner { font-size: 12px; color: #2A2A2A; margin-top: 6px; }
  .card-action { font-size: 12px; color: #2A2A2A; margin-top: 8px; font-style: italic; }
  .dist { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .dist-table { background: #FFFFFF; padding: 16px; }
  .dist-table h3 { font-size: 12px; color: #0A0A0A; margin: 0 0 8px 0; letter-spacing: 1px; }
  .dist-row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 12px; border-bottom: 1px dotted #E8DCC4; }
  .dist-row:last-child { border-bottom: none; }
  .dist-row .label { color: #2A2A2A; }
  .dist-row .val { font-weight: 600; color: #0A0A0A; }
  footer { margin-top: 48px; padding-top: 16px; border-top: 1px solid #B8965A; font-size: 10px; color: #2A2A2A; text-align: center; }
</style>
</head>
<body>

<h1>BATCH PROPERTY INTELLIGENCE</h1>
<div class="sub">Region: {{ region }} · Run: {{ timestamp }} · Elite Lifestyle Properties</div>

<h2>HEADLINE</h2>
<div class="stat-grid">
  <div class="stat">
    <div class="stat-num">{{ totals.total }}</div>
    <div class="stat-label">Total properties</div>
  </div>
  <div class="stat">
    <div class="stat-num">{{ totals.high_priority }}</div>
    <div class="stat-label">High-priority leads</div>
  </div>
  <div class="stat">
    <div class="stat-num">{{ totals.rentals }}</div>
    <div class="stat-label">Confirmed rentals</div>
  </div>
  <div class="stat">
    <div class="stat-num">{{ totals.portfolios }}</div>
    <div class="stat-label">Multi-property owners</div>
  </div>
</div>

<h2>TOP 10 SCORERS</h2>
<div class="card-grid">
{% for card in top_cards %}
  <div class="card score-{{ card.score }}">
    <div class="card-head">
      <div class="card-addr">{{ card.address }}</div>
      <div class="card-score">{{ card.score }}/10</div>
    </div>
    <div class="card-grades">Seller: {{ card.seller }} · Rental: {{ card.rental }}</div>
    <div class="card-owner"><strong>{{ card.owner }}</strong> — {{ card.classification }} · Holds {{ card.property_count }} SC properties ({{ card.rental_count }} rented)</div>
    <div class="card-action">→ {{ card.action }}</div>
  </div>
{% endfor %}
</div>

<h2>DISTRIBUTION</h2>
<div class="dist">
  <div class="dist-table">
    <h3>Seller Lead grades</h3>
    {% for label, val in seller_dist %}
    <div class="dist-row"><span class="label">{{ label }}</span><span class="val">{{ val }}</span></div>
    {% endfor %}
  </div>
  <div class="dist-table">
    <h3>Rental Lead grades</h3>
    {% for label, val in rental_dist %}
    <div class="dist-row"><span class="label">{{ label }}</span><span class="val">{{ val }}</span></div>
    {% endfor %}
  </div>
</div>

<footer>
Elite Lifestyle Properties · batch-property-intelligence · V1
</footer>

</body>
</html>
"""


def write_html_report(
    df: pd.DataFrame,
    output_path: Path,
    region_label: str,
    run_timestamp: str,
) -> None:
    """Write the HTML scan report."""
    saleable = df[~df["Non-Saleable"]]

    totals = {
        "total": len(df),
        "high_priority": int(((df["Seller Lead"] == "HIGH") | (df["Rental Lead"] == "HIGH")).sum()),
        "rentals": int((df["Owner Type"] == "Rented").sum()),
        "portfolios": int(saleable[saleable["Owner SC Property Count"] >= 2]["Owner 1 Name"].nunique()),
    }

    # Top 10 scorers
    top_10 = df.sort_values("Combined Lead Score", ascending=False).head(10)
    top_cards = []
    for _, row in top_10.iterrows():
        top_cards.append({
            "address": row["Full Address"],
            "score": int(row["Combined Lead Score"]),
            "seller": row["Seller Lead"],
            "rental": row["Rental Lead"],
            "owner": row["Owner 1 Name"],
            "classification": row.get("Owner Classification", "Unknown"),
            "property_count": int(row["Owner SC Property Count"]),
            "rental_count": int(row["Owner SC Rental Count"]),
            "action": row["Recommended Action"],
        })

    seller_dist_dict = saleable["Seller Lead"].value_counts().to_dict()
    rental_dist_dict = saleable["Rental Lead"].value_counts().to_dict()
    grade_order = ["HIGH", "MEDIUM", "LOW", "NO"]
    seller_dist = [(g, int(seller_dist_dict.get(g, 0))) for g in grade_order]
    rental_dist = [(g, int(rental_dist_dict.get(g, 0))) for g in grade_order]

    html = Template(HTML_TEMPLATE).render(
        region=region_label,
        timestamp=run_timestamp,
        totals=totals,
        top_cards=top_cards,
        seller_dist=seller_dist,
        rental_dist=rental_dist,
    )

    output_path.write_text(html, encoding="utf-8")
