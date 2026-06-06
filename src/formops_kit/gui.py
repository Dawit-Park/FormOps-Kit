from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from tkinter import Tk, filedialog, messagebox, ttk
from typing import Callable
import tkinter as tk

from .core import compile_packets


def find_project_root() -> Path:
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root)
    package_root = Path(__file__).resolve().parents[2]
    if (package_root / "examples").exists():
        return package_root
    return Path.cwd()


def default_output_dir() -> Path:
    return Path.home() / "FormOps Kit Output"


def open_folder(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.run(["open", str(path)], check=False)
    else:
        subprocess.run(["xdg-open", str(path)], check=False)


class FormOpsApp:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.project_root = find_project_root()

        self.input_csv = tk.StringVar(value=str(self.project_root / "examples" / "responses.csv"))
        self.config_json = tk.StringVar(value=str(self.project_root / "examples" / "config.json"))
        self.output_dir = tk.StringVar(value=str(default_output_dir()))
        self.status = tk.StringVar(value="Ready")

        self.root.title("FormOps Kit")
        self.root.minsize(720, 440)

        self._build()

    def _build(self) -> None:
        frame = ttk.Frame(self.root, padding=16)
        frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        title = ttk.Label(frame, text="FormOps Kit", font=("Segoe UI", 18, "bold"))
        title.grid(row=0, column=0, columnspan=3, sticky="w")

        subtitle = ttk.Label(
            frame,
            text="Turn form response CSV files into task, email, folder plan, and calendar packets.",
        )
        subtitle.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 18))

        self._path_row(frame, 2, "CSV input", self.input_csv, self._choose_csv)
        self._path_row(frame, 3, "Config JSON", self.config_json, self._choose_config)
        self._path_row(frame, 4, "Output folder", self.output_dir, self._choose_output)

        button_row = ttk.Frame(frame)
        button_row.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(16, 8))

        ttk.Button(button_row, text="Use quick-start example", command=self._use_quickstart).grid(
            row=0, column=0, padx=(0, 8)
        )
        ttk.Button(button_row, text="Compile packets", command=self._compile).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(button_row, text="Open output folder", command=self._open_output).grid(row=0, column=2)

        status_label = ttk.Label(frame, textvariable=self.status)
        status_label.grid(row=6, column=0, columnspan=3, sticky="w", pady=(8, 4))

        self.log = tk.Text(frame, height=10, wrap="word")
        self.log.grid(row=7, column=0, columnspan=3, sticky="nsew", pady=(4, 0))
        self.log.insert(
            "end",
            "1. Select a CSV file exported from a form or sheet.\n"
            "2. Select a matching config JSON file.\n"
            "3. Choose an output folder and click Compile packets.\n",
        )
        self.log.configure(state="disabled")

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(7, weight=1)

    def _path_row(
        self,
        parent: ttk.Frame,
        row: int,
        label: str,
        variable: tk.StringVar,
        command: Callable[[], None],
    ) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=8, pady=5)
        ttk.Button(parent, text="Browse", command=command).grid(row=row, column=2, sticky="e", pady=5)

    def _choose_csv(self) -> None:
        path = filedialog.askopenfilename(
            title="Choose CSV input",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.input_csv.set(path)

    def _choose_config(self) -> None:
        path = filedialog.askopenfilename(
            title="Choose config JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if path:
            self.config_json.set(path)

    def _choose_output(self) -> None:
        path = filedialog.askdirectory(title="Choose output folder")
        if path:
            self.output_dir.set(path)

    def _use_quickstart(self) -> None:
        self.input_csv.set(str(self.project_root / "examples" / "responses.csv"))
        self.config_json.set(str(self.project_root / "examples" / "config.json"))
        self.output_dir.set(str(default_output_dir()))
        self._write_log("Loaded the quick-start example paths.\n")

    def _compile(self) -> None:
        input_csv = Path(self.input_csv.get()).expanduser()
        config_json = Path(self.config_json.get()).expanduser()
        output_dir = Path(self.output_dir.get()).expanduser()

        if not input_csv.exists():
            messagebox.showerror("Missing CSV", f"CSV file does not exist:\n{input_csv}")
            return
        if not config_json.exists():
            messagebox.showerror("Missing config", f"Config file does not exist:\n{config_json}")
            return

        try:
            result = compile_packets(input_csv=input_csv, config_path=config_json, output_dir=output_dir)
        except Exception as exc:  # pragma: no cover - GUI error boundary
            self.status.set("Compile failed")
            self._write_log(f"\nCompile failed:\n{exc}\n")
            messagebox.showerror("Compile failed", str(exc))
            return

        lines = [
            "",
            "Compile complete.",
            f"Rows seen: {result.rows_seen}",
            f"Packets created: {result.packets_created}",
            f"Skipped rows: {result.skipped_rows}",
            f"Output folder: {output_dir}",
        ]
        if result.warnings:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in result.warnings)
        self.status.set(f"Created {result.packets_created} packet(s)")
        self._write_log("\n".join(lines) + "\n")
        messagebox.showinfo("FormOps Kit", f"Created {result.packets_created} packet(s).")

    def _open_output(self) -> None:
        try:
            open_folder(Path(self.output_dir.get()).expanduser())
        except Exception as exc:  # pragma: no cover - platform shell boundary
            messagebox.showerror("Could not open folder", str(exc))

    def _write_log(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.configure(state="disabled")


def main() -> None:
    try:
        root = Tk()
    except tk.TclError as exc:
        raise SystemExit(f"Could not start the FormOps Kit GUI: {exc}") from exc
    FormOpsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
