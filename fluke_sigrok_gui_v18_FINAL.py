#!/usr/bin/env python3
"""
Fluke (sigrok-cli) Live Readout — minimal CSV-only UI (polling mode)

Why polling mode?
- With fluke-dmm + '-O csv --continuous', sigrok prints the header (function/unit)
  only once at startup for some meters/firmware combos.
- When you change function on the meter (V->Ohm->A), the CSV stream can keep
  emitting only numeric lines, so the UI never learns the new unit/mode.
- Polling (one sample per run, repeated) re-reads the header each time, so
  function changes are detected reliably.

Command used (per poll):
  sigrok-cli -d fluke-dmm:conn=COMx -C P1 --samples 1 -O csv

Notes:
- Driver supports config options: continuous, limit_samples, limit_time
- We use --samples 1 for fast, deterministic polls.
"""


APP_VERSION = "v18"

# Embedded app icon (JPEG)
ICON_B64 = """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"""

def _app_icon() -> QIcon:
    try:
        data = base64.b64decode(ICON_B64)
        pix = QPixmap()
        pix.loadFromData(data)
        return QIcon(pix)
    except Exception:
        return QIcon()


import os
import re
import sys
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt, QProcess, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

# Optional: nice COM port labels via pyserial
try:
    from serial.tools import list_ports  # type: ignore
except Exception:
    list_ports = None


_FLOAT_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")

# sigrok / MSVCRT-style float sentinel strings we may see on Windows.
# These are not parseable by float() and should be treated as invalid/overload.
_SPECIAL_FLOAT_TOKENS = {
    "1.#inf", "-1.#inf",
    "1.#ind", "-1.#ind",
    "1.#nan", "-1.#nan",
    "1.#qnan", "-1.#qnan",
}

# Basic unit token matcher (first token in CSV header lines).
_UNIT_TOKEN_RE = re.compile(
    r"^(?P<prefix>[pnumkMGT]?)(?P<unit>V|A|F|Hz|%|Ω|Ohm|ohm|°C|°F)$"
)


def _is_special_float_token(s: str) -> bool:
    return s.strip().lower() in _SPECIAL_FLOAT_TOKENS


def _is_float_token(s: str) -> bool:
    return bool(_FLOAT_RE.match(s.strip()))


def _is_overload_token(s: str) -> bool:
    t = s.strip().lower()
    return t in {
        "1.#inf", "-1.#inf",
        "1.#ind", "-1.#ind",
        "1.#nan", "-1.#nan",
        "1.#qnan", "-1.#qnan",
        "inf", "-inf",
        "nan", "-nan",
        "ol", "over", "overload",
    }


_UNIT_TOKEN_RE = re.compile(
    r"^(?P<prefix>[pnumkMGT]?)(?P<unit>(?:V|A|F|Hz|%|Ω|Ohm|ohm|S|H|W|VA|VAR|°C|°F|C|F))$"
)


def _parse_header_line(header_line: str) -> Tuple[str, str]:
    """Parse a CSV header line like 'V DC', 'Ω', 'F', 'A DC', etc.

    Returns: (unit_symbol, mode_text)
    - unit_symbol is a short unit like V, A, Ω, F, Hz, °C, ...
    - mode_text is the remainder (e.g. 'DC', 'AC RMS'), or '' if none
    """
    h = header_line.strip()
    if not h:
        return "", ""

    # Normalize multiple spaces
    h = " ".join(h.split())

    # Split into tokens. First token is usually the unit.
    parts = h.split(" ", 1)
    u = _normalize_unit(parts[0])
    mode = parts[1] if len(parts) > 1 else ""

    # Normalize common unit tokens
    # (sigrok sometimes emits UTF symbols or text; keep them as-is for display)
    if u.lower() == "ohm":
        u = "Ω"

    # Some devices duplicate the unit (e.g. 'Ω'). Remove that from mode.
    if u and mode:
        m_norm = " ".join(mode.split())
        if m_norm == f"{u} {u}" or m_norm.replace(" ", "") == (u * 2) or m_norm == u:
            mode = ""
        if u == "Ω" and m_norm.lower().replace(" ", "") in ("ohmohm", "omegaomega"):
            mode = ""

    return u, mode



def _normalize_unit(u: str) -> str:
    """Normalize unit strings coming from sigrok (handles unicode ohm sign, micro, etc.)."""
    if not u:
        return u
    # libsigrok / sigrok-cli may emit U+2126 OHM SIGN (Ω); normalize to Greek Omega (Ω)
    u = u.replace("Ω", "Ω")
    # Normalize micro prefix to the common 'µ'
    u = u.replace("uA", "µA").replace("uF", "µF")
    # Some headers may spell out Ohm
    if u == "Ohm":
        u = "Ω"
    return u

def _choose_si_prefix(value: float, unit: str) -> tuple[float, str]:
    """Scale value and return (scaled_value, prefix_string) for SI-display.

    We intentionally auto-scale for units where Fluke ranges commonly change:
      V, A, Ω, F.
    """
    if unit not in {"V", "A", "Ω", "F"}:
        return value, ""
    if value == 0:
        return 0.0, ""

    abs_v = abs(value)
    # Ordered from smallest to largest.
    steps = [
        (1e-12, "p"),
        (1e-9, "n"),
        (1e-6, "µ"),
        (1e-3, "m"),
        (1.0, ""),
        (1e3, "k"),
        (1e6, "M"),
        (1e9, "G"),
        (1e12, "T"),
    ]

    # Find the largest factor that keeps scaled >= 1.0 (but not too big).
    chosen_factor = 1.0
    chosen_prefix = ""
    for factor, prefix in steps:
        if abs_v >= factor:
            chosen_factor = factor
            chosen_prefix = prefix

    scaled = value / chosen_factor
    # If scaled is still too small (<1) pick one step down (when possible)
    if abs(scaled) < 1.0:
        for factor, prefix in steps:
            if abs_v >= factor:
                chosen_factor = factor
                chosen_prefix = prefix
            if abs_v < factor:
                break
        scaled = value / chosen_factor

    # Cap: if scaled is >= 1000, move up one prefix to keep it tidy.
    if abs(scaled) >= 1000:
        for i, (factor, prefix) in enumerate(steps):
            if factor == chosen_factor and i + 1 < len(steps):
                chosen_factor, chosen_prefix = steps[i + 1]
                scaled = value / chosen_factor
                break

    return scaled, chosen_prefix


def _choose_si_unit(value: float, unit: str) -> tuple[float, str]:
    """Return (scaled_value, unit_display) using SI prefixes.

    libsigrok sometimes uses 'OHM' instead of 'Ω' in headers.
    """
    unit_disp = "Ω" if unit and unit.upper() == "OHM" else unit
    scaled, prefix = _choose_si_prefix(value, unit_disp)
    return scaled, f"{prefix}{unit_disp}" if unit_disp else ""


def _format_value(value: float | None, overload: bool) -> str:
    if overload or value is None:
        return "OL"
    return f"{value:.4f}"


def _find_sigrok_default() -> str:
    candidates = [
        r"C:\Program Files\sigrok\sigrok-cli\sigrok-cli.exe",
        r"C:\Program Files (x86)\sigrok\sigrok-cli\sigrok-cli.exe",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return ""


def list_com_ports() -> list[tuple[str, str]]:
    ports: list[tuple[str, str]] = []
    if list_ports is None:
        for i in range(1, 33):
            ports.append((f"COM{i}", f"COM{i}"))
        return ports

    for p in list_ports.comports():
        device = getattr(p, "device", "") or ""
        desc = getattr(p, "description", "") or device
        ports.append((device, f"{device} - {desc}"))
    return ports


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowIcon(_app_icon())
        self.setWindowTitle(f"Fluke (sigrok-cli) Live Readout {APP_VERSION}")
        # Set app icon if the file is рядом with this script
        try:
            # Look for the icon next to the script first, then in CWD.
            candidates = [
                Path(__file__).with_name("avatar small.jpg"),
                Path.cwd() / "avatar small.jpg",
                Path(__file__).with_name("avatar_small.jpg"),
                Path.cwd() / "avatar_small.jpg",
            ]
            for icon_path in candidates:
                if icon_path.exists():
                    self.setWindowIcon(QIcon(str(icon_path)))
                    break
            else:
                # Fallback: embedded tiny PNG (so the app never shows the generic Qt icon).
                import base64
                png_b64 = (
                    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAUElEQVR4nGNgoBAw4pH7T4xabILoGvHqYSJRM4YaJlwSxBqC7gKSAcwAUmxHcQXVXDDwBuBLULgAI1VdQKor4GrRXUCMIYw4OWiAqMxEMQAAu5sJGu3mfCwAAAAASUVORK5CYII="
                )
                self.setWindowIcon(QIcon(QtGui.QPixmap.fromImage(QtGui.QImage.fromData(base64.b64decode(png_b64)))))
        except Exception:
            pass

        self.proc = QProcess(self)
        self.proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.proc.readyReadStandardOutput.connect(self.on_ready_read)
        self.proc.finished.connect(self.on_proc_finished)

        # Polling engine
        self.running = False
        self.poll_inflight = False
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(250)  # ms; adjust later if needed
        self.poll_timer.timeout.connect(self.poll_once)

        # UI state
        self.last_sample_dt: datetime | None = None
        self.value_text = "—"
        self.header_raw = ""
        self.header_text = ""
        self.header_small = ""

        # Recording
        self.rec_fp = None

        self._build_ui()
        self.refresh_ports()

        self.sigrok_path_edit.setText(_find_sigrok_default())
        self.record_check.setChecked(False)
        self.on_record_toggled(False)

        self.update_ui_state(running=False)

    # ---------------- UI ----------------

    def _build_ui(self) -> None:
        tabs = QTabWidget()

        # Live tab (minimal)
        live = QWidget()
        live_layout = QVBoxLayout(live)

        conn_box = QGroupBox("Connection")
        conn_grid = QGridLayout(conn_box)

        # Minimal: driver is fixed (fluke-dmm), so only show the COM port.
        conn_grid.addWidget(QLabel("COM Port:"), 0, 0)
        self.com_combo = QComboBox()
        conn_grid.addWidget(self.com_combo, 0, 1, 1, 3)

        self.refresh_btn = QPushButton("Refresh ports")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        conn_grid.addWidget(self.refresh_btn, 0, 4)

        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)

        conn_grid.addWidget(self.start_btn, 1, 3)
        conn_grid.addWidget(self.stop_btn, 1, 4)

        live_layout.addWidget(conn_box)

        # Readout only (no Status box)
        readout_box = QGroupBox("Readout")
        readout_layout = QVBoxLayout(readout_box)
        readout_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.value_big = QLabel("—")
        f = QFont()
        f.setPointSize(56)
        f.setBold(True)
        self.value_big.setFont(f)
        self.value_big.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.header_big = QLabel("")
        f2 = QFont()
        f2.setPointSize(18)
        self.header_big.setFont(f2)
        self.header_big.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.header_small_lbl = QLabel("")
        f3 = QFont()
        f3.setPointSize(10)
        self.header_small_lbl.setFont(f3)
        self.header_small_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        readout_layout.addStretch(1)
        readout_layout.addWidget(self.value_big)
        readout_layout.addSpacing(6)
        readout_layout.addWidget(self.header_big)
        readout_layout.addWidget(self.header_small_lbl)
        readout_layout.addStretch(1)

        live_layout.addWidget(readout_box, 1)

        # Settings tab
        settings = QWidget()
        s_layout = QVBoxLayout(settings)

        backend_box = QGroupBox("Backend / Recording")
        b_grid = QGridLayout(backend_box)

        self.sigrok_path_edit = QLineEdit()
        self.sigrok_browse_btn = QPushButton("Browse…")
        self.sigrok_browse_btn.clicked.connect(self.browse_sigrok)

        self.record_check = QCheckBox("Record CSV to file")
        self.csv_path_edit = QLineEdit()
        self.csv_path_edit.setPlaceholderText("CSV path (write while recording)")
        self.csv_browse_btn = QPushButton("…")
        self.csv_browse_btn.clicked.connect(self.browse_csv_path)

        self.record_check.toggled.connect(self.on_record_toggled)

        b_grid.addWidget(QLabel("sigrok-cli.exe:"), 0, 0)
        b_grid.addWidget(self.sigrok_path_edit, 0, 1, 1, 3)
        b_grid.addWidget(self.sigrok_browse_btn, 0, 4)

        b_grid.addWidget(self.record_check, 1, 0, 1, 2)
        b_grid.addWidget(self.csv_path_edit, 1, 2, 1, 2)
        b_grid.addWidget(self.csv_browse_btn, 1, 4)

        # Poll interval control (optional later) — keep hidden for now
        s_layout.addWidget(backend_box)
        s_layout.addStretch(1)

        tabs.addTab(live, "Live")
        tabs.addTab(settings, "Settings")

        self.setCentralWidget(tabs)
        self.resize(860, 520)

    # ---------------- Helpers ----------------

    def refresh_ports(self) -> None:
        current = self.current_com_port()
        self.com_combo.clear()
        ports = list_com_ports()
        if not ports:
            ports = [(f"COM{i}", f"COM{i}") for i in range(1, 33)]
        for dev, label in ports:
            self.com_combo.addItem(label, dev)
        if current:
            idx = self.com_combo.findData(current)
            if idx >= 0:
                self.com_combo.setCurrentIndex(idx)

    def current_com_port(self) -> str:
        data = self.com_combo.currentData()
        return str(data) if data else ""

    def browse_sigrok(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select sigrok-cli.exe", "", "Executable (*.exe);;All files (*.*)")
        if path:
            self.sigrok_path_edit.setText(path)

    def browse_csv_path(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Choose CSV output file", "", "CSV (*.csv);;All files (*.*)")
        if path:
            self.csv_path_edit.setText(path)

    def on_record_toggled(self, enabled: bool) -> None:
        self.csv_path_edit.setEnabled(enabled)
        self.csv_browse_btn.setEnabled(enabled)

    def update_ui_state(self, running: bool) -> None:
        self.start_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)
        self.com_combo.setEnabled(not running)
        self.refresh_btn.setEnabled(not running)

    def _close_recording(self) -> None:
        if self.rec_fp is not None:
            try:
                self.rec_fp.close()
            except Exception:
                pass
            self.rec_fp = None

    # ---------------- Start/Stop ----------------

    def start(self) -> None:
        sigrok = self.sigrok_path_edit.text().strip()
        if not sigrok or not os.path.isfile(sigrok):
            QMessageBox.critical(self, "sigrok-cli not found", "Please select a valid sigrok-cli.exe path in Settings.")
            return

        com = self.current_com_port()
        if not com:
            QMessageBox.critical(self, "No COM port", "Please select a COM port.")
            return

        # Prepare recording
        self._close_recording()
        if self.record_check.isChecked():
            out_path = self.csv_path_edit.text().strip()
            if not out_path:
                out_path = os.path.join(os.getcwd(), f"fluke_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
                self.csv_path_edit.setText(out_path)
            try:
                self.rec_fp = open(out_path, "a", encoding="utf-8", newline="\n")
            except Exception as e:
                QMessageBox.critical(self, "Cannot open CSV file", f"Failed to open CSV file:\n{out_path}\n\n{e}")
                self.rec_fp = None
                return

        # Reset displayed values
        self.value_text = "—"
        self.header_text = ""
        self.header_small = ""
        self.last_sample_dt = None
        self._apply_readout()

        self.running = True
        self.poll_inflight = False
        self.update_ui_state(running=True)

        # Kick off immediately, then timer keeps it going
        self.poll_once()
        self.poll_timer.start()

    def stop(self) -> None:
        self.running = False
        self.poll_timer.stop()

        if self.proc.state() != QProcess.ProcessState.NotRunning:
            self.proc.terminate()
            if not self.proc.waitForFinished(1200):
                self.proc.kill()
                self.proc.waitForFinished(1200)

        self.poll_inflight = False
        self._close_recording()
        self.update_ui_state(running=False)

    # ---------------- Polling ----------------

    def poll_once(self) -> None:
        if not self.running:
            return
        if self.poll_inflight:
            return
        if self.proc.state() != QProcess.ProcessState.NotRunning:
            return

        sigrok = self.sigrok_path_edit.text().strip()
        com = self.current_com_port()

        # One-sample acquisition; this forces sigrok to emit the current header each time.
        args = [
            "-d", f"fluke-dmm:conn={com}",
            "-C", "P1",
            "--samples", "1",
            "-O", "csv",
        ]
        self.poll_inflight = True
        self.proc.start(sigrok, args)

    # ---------------- Process parsing ----------------

    def on_ready_read(self) -> None:
        try:
            chunk = bytes(self.proc.readAllStandardOutput()).decode("utf-8", errors="replace")
        except Exception:
            return

        for raw_line in chunk.splitlines():
            line = raw_line.strip("\r\n")
            if not line:
                continue

            # Record raw line as-is if enabled
            if self.rec_fp is not None:
                try:
                    self.rec_fp.write(line + "\n")
                    self.rec_fp.flush()
                except Exception:
                    pass

            # Hide driver noise always
            if line.startswith("sr:") or line.startswith("srd:") or line.startswith("WARNING:") or line.startswith("ERROR:"):
                continue

            # CSV comments
            if line.lstrip().startswith(";"):
                continue

            token = line.strip()

            # Header / function line comes before the numeric sample in typical CSV output.
            # e.g. "V DC", "MΩ", "A AC", "F", "Hz".
            # NOTE: Windows may emit "1.#QNAN" / "1.#INF" etc; those are handled as overload
            # tokens by _is_overload_token() and must NOT be treated as headers.
            if not _is_float_token(token) and not _is_overload_token(token):
                self.header_raw = token
                # Don't update the UI yet; wait for the value line so we can scale units.
                continue

            # Value line
            if _is_overload_token(token):
                # Keep the current header_raw/header_text; show overload clearly.
                unit_sym, mode = _parse_header_line(self.header_raw)
                unit_disp = {"Ohm": "Ω", "degC": "°C", "degF": "°F"}.get(unit_sym, unit_sym) or self.header_raw or ""
                self.header_text = f"{unit_disp} {mode}".strip() if (mode and mode != unit_disp) else unit_disp
                self.header_small = mode if (mode and mode != unit_disp) else ""

                self.value_text = "OL"
                self.last_sample_dt = datetime.now()
                self._apply_readout()
                continue

            if _is_float_token(token):
                try:
                    v = float(token)
                except Exception:
                    continue

                unit_sym, mode = _parse_header_line(self.header_raw)
                unit_disp = {"Ohm": "Ω", "degC": "°C", "degF": "°F"}.get(unit_sym, unit_sym)

                if unit_disp == "Ω":
                    # For resistance, show kΩ/MΩ when value is large.
                    av = abs(v)
                    if av >= 1e6:
                        scaled_v, unit_disp = (v / 1e6), "MΩ"
                    elif av >= 1e3:
                        scaled_v, unit_disp = (v / 1e3), "kΩ"
                    else:
                        scaled_v = v
                else:
                    scaled_v, unit_disp = _choose_si_unit(v, unit_disp)
                # If we couldn't parse a unit from the header, fall back to showing the raw header.
                if not unit_disp:
                    unit_disp = unit_sym or self.header_raw

                self.value_text = f"{scaled_v:.4f}"
                self.header_text = f"{unit_disp} {mode}".strip() if (mode and mode != unit_disp) else unit_disp
                self.header_small = mode if (mode and mode != unit_disp) else ""

                self.last_sample_dt = datetime.now()
                self._apply_readout()
                continue

    def on_proc_finished(self, code: int, status) -> None:
        # Mark poll as complete; next timer tick will start a new run.
        self.poll_inflight = False

        # If sigrok fails repeatedly (wrong COM / interface unplugged), stop gracefully.
        if self.running and code != 0:
            # Don't spam dialogs; just stop after a single failure.
            self.stop()
            QMessageBox.critical(
                self,
                "sigrok-cli error",
                f"sigrok-cli exited with code {code}.\n\n"
                "Check that the meter interface is connected and the correct COM port is selected.",
            )

    def _apply_readout(self) -> None:
        self.value_big.setText(self.value_text or "—")
        self.header_big.setText(self.header_text or "")
        self.header_small_lbl.setText(self.header_small or "")


def main() -> int:
    # Improve taskbar icon on Windows
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(f"fluke.sigrok.readout.{APP_VERSION}")
    except Exception:
        pass

    app = QApplication(sys.argv)
    try:
        app.setWindowIcon(_load_icon())
    except Exception:
        pass
    w = MainWindow()
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
