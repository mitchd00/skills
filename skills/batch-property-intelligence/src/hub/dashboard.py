"""
Master dashboard regeneration.

Writes outputs/BPI_Master_Dashboard_V<N>_<DD-MM-YYYY_HHMM>.{xlsx,html} from
the current state of the DB after a recompute. Archives the prior versioned
files into outputs/Archive/ per ELP rules and refreshes the unversioned
'_latest' aliases the launcher button opens.
"""

import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.output.excel import write_excel
from src.output.html_report import write_html_report


REGION_LABEL = "BPI Master Dashboard"


def _next_version(output_dir: Path) -> int:
    """Find the highest V<N> already in outputs/ or outputs/Archive/, return N+1."""
    candidates = list(output_dir.glob("BPI_Master_Dashboard_V*.xlsx"))
    archive_dir = output_dir / "Archive"
    if archive_dir.exists():
        candidates.extend(archive_dir.glob("BPI_Master_Dashboard_V*.xlsx"))
    highest = 0
    for p in candidates:
        try:
            v = int(p.stem.split("_V")[1].split("_")[0])
            highest = max(highest, v)
        except (IndexError, ValueError):
            continue
    return highest + 1


def _archive_prior(output_dir: Path) -> None:
    """Move every prior versioned dashboard file into outputs/Archive/."""
    archive_dir = output_dir / "Archive"
    archive_dir.mkdir(exist_ok=True)
    for pattern in ("BPI_Master_Dashboard_V*.xlsx", "BPI_Master_Dashboard_V*.html"):
        for path in output_dir.glob(pattern):
            shutil.move(str(path), str(archive_dir / path.name))


def regenerate_dashboard(
    df_final: pd.DataFrame,
    output_dir: Path,
    region_label: str = REGION_LABEL,
) -> dict:
    """
    Render the master Excel + HTML dashboard from a fully-scored dataframe
    (produced by recompute.recompute_all). Archives any prior dashboard
    files first, writes the new versioned pair, then refreshes the
    '_latest' aliases.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    _archive_prior(output_dir)

    version = _next_version(output_dir)
    timestamp = datetime.now().strftime("%d-%m-%Y_%H%M")
    xlsx_name = f"BPI_Master_Dashboard_V{version}_{timestamp}.xlsx"
    html_name = f"BPI_Master_Dashboard_V{version}_{timestamp}.html"
    xlsx_path = output_dir / xlsx_name
    html_path = output_dir / html_name

    write_excel(df_final, xlsx_path, region_label, timestamp)
    write_html_report(df_final, html_path, region_label, timestamp)

    # _latest aliases — copies, not symlinks, so they work cleanly on Windows
    shutil.copy(xlsx_path, output_dir / "BPI_Master_Dashboard_latest.xlsx")
    shutil.copy(html_path, output_dir / "BPI_Master_Dashboard_latest.html")

    return {
        "version": version,
        "timestamp": timestamp,
        "xlsx_path": str(xlsx_path),
        "html_path": str(html_path),
    }
