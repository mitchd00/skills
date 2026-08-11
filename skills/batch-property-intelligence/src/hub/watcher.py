"""
Folder watcher — the heart of the Hub.

Watches an inputs/ folder for new CSVs. Each CSV that lands triggers:
ingest → recompute (full DB) → dashboard regen → status update.

A 1.5-second debounce settles partial writes from RP Data's download
(Chrome writes incrementally) before processing. Files already in the
folder at startup are processed once each.
"""

import logging
import threading
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from src.hub.db import DEFAULT_DB_PATH, connect, db_stats
from src.hub.dashboard import regenerate_dashboard
from src.hub.ingest import ingest_csv
from src.hub.recompute import recompute_all
from src.hub.status import write_status


DEBOUNCE_SECONDS = 1.5
LOG_PATH = Path("data/bpi.log")


def _configure_logging():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def process_csv(
    csv_path: Path,
    db_path: Path,
    config_path: Path,
    output_dir: Path,
) -> None:
    """Run the full ingest → recompute → dashboard chain for one CSV."""
    log = logging.getLogger(__name__)
    log.info("Ingesting %s", csv_path.name)
    delta = ingest_csv(csv_path, db_path, region_hint=csv_path.stem)
    log.info(
        "Ingested %s rows (new parcels: %d, new sales: %d)",
        delta["rows_in_csv"], delta["new_parcels"], delta["new_sales"],
    )

    log.info("Recomputing scores across full DB")
    summary = recompute_all(db_path, config_path)
    if summary.get("empty"):
        log.warning("DB is empty after ingest — skipping dashboard")
        return
    log.info(
        "Recompute complete: %d saleable parcels, %d HIGH seller leads, %d HIGH rental leads, %d portfolios (2+)",
        summary["saleable_parcels"], summary["seller_high"],
        summary["rental_high"], summary["owners_2plus"],
    )

    log.info("Regenerating master dashboard")
    dash = regenerate_dashboard(summary["df_final"], output_dir)
    log.info("Dashboard V%d written: %s", dash["version"], dash["xlsx_path"])

    with connect(db_path) as conn:
        stats = db_stats(conn)
    write_status(
        state="idle",
        last_event=(
            f"{csv_path.name}: +{delta['new_parcels']} parcels, "
            f"+{delta['new_sales']} sales → V{dash['version']}"
        ),
        db_stats=stats,
    )


class _Handler(FileSystemEventHandler):
    def __init__(self, db_path: Path, config_path: Path, output_dir: Path):
        self.db_path = db_path
        self.config_path = config_path
        self.output_dir = output_dir
        self._pending: dict[Path, threading.Timer] = {}
        self._lock = threading.Lock()

    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() != ".csv":
            return
        self._schedule(path)

    def on_modified(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() != ".csv":
            return
        self._schedule(path)

    def _schedule(self, path: Path) -> None:
        with self._lock:
            existing = self._pending.pop(path, None)
            if existing is not None:
                existing.cancel()
            timer = threading.Timer(DEBOUNCE_SECONDS, self._fire, args=(path,))
            self._pending[path] = timer
            timer.start()

    def _fire(self, path: Path) -> None:
        with self._lock:
            self._pending.pop(path, None)
        if not path.exists():
            return
        try:
            write_status(state="processing", last_event=f"Processing {path.name}")
            process_csv(path, self.db_path, self.config_path, self.output_dir)
        except Exception as exc:
            logging.getLogger(__name__).exception("Failed to process %s", path)
            write_status(state="error", last_event=f"{path.name}: {exc}")


def run_watcher(
    inputs_dir: Path = Path("inputs"),
    outputs_dir: Path = Path("outputs"),
    db_path: Path = DEFAULT_DB_PATH,
    config_path: Path = Path("config/scoring-weights.yaml"),
) -> None:
    """Blocking call — runs the watcher until interrupted."""
    _configure_logging()
    log = logging.getLogger(__name__)

    inputs_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    log.info("BPI Hub watcher starting on %s", inputs_dir.resolve())
    write_status(state="starting", last_event=f"Watching {inputs_dir.resolve()}")

    handler = _Handler(db_path, config_path, outputs_dir)
    observer = Observer()
    observer.schedule(handler, str(inputs_dir), recursive=False)
    observer.start()

    # Process any files already in inputs/ at startup
    existing = sorted(inputs_dir.glob("*.csv"))
    if existing:
        log.info("Found %d CSV(s) already in inputs/ — processing", len(existing))
        for csv_path in existing:
            try:
                write_status(state="processing", last_event=f"Processing {csv_path.name}")
                process_csv(csv_path, db_path, config_path, outputs_dir)
            except Exception:
                log.exception("Failed to process existing %s", csv_path)

    with connect(db_path) as conn:
        stats = db_stats(conn)
    write_status(state="idle", last_event="Watcher idle", db_stats=stats)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Watcher stopping (KeyboardInterrupt)")
    finally:
        observer.stop()
        observer.join()
        write_status(state="stopped", last_event="Watcher stopped")
