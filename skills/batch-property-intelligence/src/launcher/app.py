"""
Tkinter launcher window for the BPI Intelligence Hub.

Stdlib only — no tkinterdnd2 dep. Buttons start/stop the watcher
subprocess, copy a picked CSV into inputs/, open the latest dashboard,
and reveal the inputs/outputs folders. Polls data/status.json once per
second for the status pane and tails data/bpi.log for the log pane.

Designed to be packaged as a single Windows .exe via PyInstaller
(see build/bpi-launcher.spec).
"""

import os
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext

from src.hub.status import read_status


APP_TITLE = "Batch Property Intelligence — ELP"
POLL_INTERVAL_MS = 1000
LOG_TAIL_LINES = 20


def _resolve_project_root() -> Path:
    """Project root = parent of src/. Works whether run as `python -m src.launcher.app`,
    via the bpi-launcher script entry, or from a frozen PyInstaller bundle."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent.resolve()
    return Path(__file__).resolve().parents[2]


def _open_in_os(path: Path) -> None:
    """Open a file or folder in the OS default handler."""
    if not path.exists():
        messagebox.showerror(APP_TITLE, f"Not found:\n{path}")
        return
    if sys.platform == "win32":
        os.startfile(str(path))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


class LauncherApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.project_root = _resolve_project_root()
        self.inputs_dir = self.project_root / "inputs"
        self.outputs_dir = self.project_root / "outputs"
        self.data_dir = self.project_root / "data"
        self.pid_file = self.data_dir / "watcher.pid"
        self.log_file = self.data_dir / "bpi.log"

        for d in (self.inputs_dir, self.outputs_dir, self.data_dir):
            d.mkdir(parents=True, exist_ok=True)

        self.watcher_proc: subprocess.Popen | None = None
        self._build_ui()
        self._poll()

    def _build_ui(self) -> None:
        self.root.title(APP_TITLE)
        self.root.geometry("760x520")
        self.root.minsize(640, 440)

        header = tk.Frame(self.root, bg="#0A0A0A", padx=16, pady=12)
        header.pack(fill="x")
        tk.Label(
            header, text="BATCH PROPERTY INTELLIGENCE",
            fg="#F7F4EE", bg="#0A0A0A",
            font=("Arial", 13, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header, text="Elite Lifestyle Properties — Intelligence Hub",
            fg="#B8965A", bg="#0A0A0A",
            font=("Arial", 9, "italic"),
        ).pack(anchor="w")

        status_frame = tk.Frame(self.root, padx=16, pady=12, bg="#F7F4EE")
        status_frame.pack(fill="x")

        self.status_var = tk.StringVar(value="Watcher: ○ stopped")
        tk.Label(
            status_frame, textvariable=self.status_var,
            font=("Arial", 11, "bold"), bg="#F7F4EE", fg="#0A0A0A",
        ).pack(anchor="w")

        self.last_event_var = tk.StringVar(value="No activity yet.")
        tk.Label(
            status_frame, textvariable=self.last_event_var,
            font=("Arial", 9), bg="#F7F4EE", fg="#2A2A2A",
            wraplength=700, justify="left",
        ).pack(anchor="w", pady=(4, 0))

        self.db_stats_var = tk.StringVar(value="DB: 0 parcels · 0 sales · 0 owners · 0 runs")
        tk.Label(
            status_frame, textvariable=self.db_stats_var,
            font=("Arial", 9), bg="#F7F4EE", fg="#2A2A2A",
        ).pack(anchor="w", pady=(2, 0))

        button_frame = tk.Frame(self.root, padx=16, pady=8)
        button_frame.pack(fill="x")

        def make_btn(text, cmd, col):
            b = tk.Button(button_frame, text=text, command=cmd, width=20, font=("Arial", 9))
            b.grid(row=0, column=col, padx=4, pady=4, sticky="ew")
            return b

        self.start_btn = make_btn("Start Watcher", self._start_watcher, 0)
        self.stop_btn = make_btn("Stop Watcher", self._stop_watcher, 1)
        make_btn("Pick CSV…", self._pick_csv, 2)
        make_btn("Open Dashboard", self._open_dashboard, 3)

        button_frame_2 = tk.Frame(self.root, padx=16, pady=0)
        button_frame_2.pack(fill="x")

        def make_btn2(text, cmd, col):
            b = tk.Button(button_frame_2, text=text, command=cmd, width=20, font=("Arial", 9))
            b.grid(row=0, column=col, padx=4, pady=4, sticky="ew")
            return b

        make_btn2("Open Inputs Folder", lambda: _open_in_os(self.inputs_dir), 0)
        make_btn2("Open Outputs Folder", lambda: _open_in_os(self.outputs_dir), 1)
        make_btn2("Rebuild Dashboard", self._rebuild_now, 2)
        make_btn2("Quit", self._on_close, 3)

        log_frame = tk.Frame(self.root, padx=16, pady=8)
        log_frame.pack(fill="both", expand=True)
        tk.Label(log_frame, text="Activity log", font=("Arial", 9, "bold"), anchor="w").pack(fill="x")
        self.log_widget = scrolledtext.ScrolledText(
            log_frame, height=10, font=("Consolas", 9), bg="#FFFFFF", fg="#2A2A2A", state="disabled",
        )
        self.log_widget.pack(fill="both", expand=True, pady=(4, 0))

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _start_watcher(self) -> None:
        if self.watcher_proc and self.watcher_proc.poll() is None:
            messagebox.showinfo(APP_TITLE, "Watcher already running.")
            return
        cmd = [sys.executable, "-m", "src.main", "watch"]
        try:
            self.watcher_proc = subprocess.Popen(cmd, cwd=str(self.project_root))
            self.pid_file.write_text(str(self.watcher_proc.pid), encoding="utf-8")
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"Failed to start watcher:\n{exc}")

    def _stop_watcher(self) -> None:
        if not self.watcher_proc or self.watcher_proc.poll() is not None:
            messagebox.showinfo(APP_TITLE, "Watcher is not running.")
            return
        try:
            self.watcher_proc.terminate()
            self.watcher_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.watcher_proc.kill()
        finally:
            self.watcher_proc = None
            if self.pid_file.exists():
                self.pid_file.unlink()

    def _pick_csv(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Pick RP Data CSV(s) to add to the Hub",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not paths:
            return
        for src in paths:
            src_path = Path(src)
            dst_path = self.inputs_dir / src_path.name
            try:
                shutil.copy(src_path, dst_path)
            except Exception as exc:
                messagebox.showerror(APP_TITLE, f"Failed to copy {src_path.name}:\n{exc}")
                return
        messagebox.showinfo(
            APP_TITLE,
            f"Copied {len(paths)} file(s) into inputs/.\n"
            "If the watcher is running it will process them automatically.\n"
            "If not, click Start Watcher.",
        )

    def _open_dashboard(self) -> None:
        latest = self.outputs_dir / "BPI_Master_Dashboard_latest.html"
        if not latest.exists():
            messagebox.showinfo(
                APP_TITLE,
                "No dashboard yet. Drop a CSV into inputs/ (or click Pick CSV…)\n"
                "and start the watcher.",
            )
            return
        webbrowser.open(latest.as_uri())

    def _rebuild_now(self) -> None:
        def run():
            try:
                subprocess.run(
                    [sys.executable, "-m", "src.main", "rebuild"],
                    cwd=str(self.project_root), check=True,
                )
            except subprocess.CalledProcessError as exc:
                self.root.after(0, lambda: messagebox.showerror(APP_TITLE, f"Rebuild failed:\n{exc}"))
        threading.Thread(target=run, daemon=True).start()

    def _poll(self) -> None:
        status = read_status(self.data_dir / "status.json")
        running = self.watcher_proc is not None and self.watcher_proc.poll() is None
        dot = "●" if running else "○"
        state = status.get("state", "unknown")
        self.status_var.set(f"Watcher: {dot} {state}")
        if status.get("last_event"):
            self.last_event_var.set(f"Last: {status['last_event']}")
        db = status.get("db") or {}
        self.db_stats_var.set(
            f"DB: {db.get('parcels', 0)} parcels · {db.get('sales', 0)} sales · "
            f"{db.get('owners', 0)} owners · {db.get('runs', 0)} runs"
        )

        self._refresh_log()
        self.root.after(POLL_INTERVAL_MS, self._poll)

    def _refresh_log(self) -> None:
        if not self.log_file.exists():
            return
        try:
            lines = self.log_file.read_text(encoding="utf-8").splitlines()[-LOG_TAIL_LINES:]
        except Exception:
            return
        self.log_widget.configure(state="normal")
        self.log_widget.delete("1.0", "end")
        self.log_widget.insert("end", "\n".join(lines))
        self.log_widget.see("end")
        self.log_widget.configure(state="disabled")

    def _on_close(self) -> None:
        if self.watcher_proc and self.watcher_proc.poll() is None:
            if messagebox.askyesno(APP_TITLE, "Watcher is running. Stop it and quit?"):
                self._stop_watcher()
            else:
                return
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    LauncherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
