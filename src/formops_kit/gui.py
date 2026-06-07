from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from tkinter import Tk, filedialog, messagebox, ttk
from typing import Callable
import tkinter as tk

from .core import compile_packets_from_config
from .presets import WorkflowPreset, default_preset, list_presets, write_preset_files


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
        self.presets = list_presets()
        self.preset_by_label = {preset.label: preset for preset in self.presets}

        self.selected_preset = tk.StringVar(value=default_preset().label)
        self.preset_description = tk.StringVar(value=default_preset().description)
        self.input_csv = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.status = tk.StringVar(value="준비됨")

        self.root.title("FormOps Kit")
        self.root.minsize(760, 500)

        self._build()
        self._load_sample(open_after=False)

    def _build(self) -> None:
        frame = ttk.Frame(self.root, padding=16)
        frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        title = ttk.Label(frame, text="FormOps Kit", font=("Malgun Gothic", 18, "bold"))
        title.grid(row=0, column=0, columnspan=3, sticky="w")

        subtitle = ttk.Label(
            frame,
            text="폼/시트 CSV를 처리 체크리스트, 답장 초안, 폴더 계획, 캘린더 파일로 정리합니다.",
        )
        subtitle.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 18))

        ttk.Label(frame, text="업무 유형").grid(row=2, column=0, sticky="w", pady=5)
        preset_box = ttk.Combobox(
            frame,
            textvariable=self.selected_preset,
            values=[preset.label for preset in self.presets],
            state="readonly",
        )
        preset_box.grid(row=2, column=1, columnspan=2, sticky="ew", padx=8, pady=5)
        preset_box.bind("<<ComboboxSelected>>", self._preset_changed)

        description = ttk.Label(frame, textvariable=self.preset_description, wraplength=560)
        description.grid(row=3, column=1, columnspan=2, sticky="w", padx=8, pady=(0, 8))

        self._path_row(frame, 4, "CSV 파일", self.input_csv, self._choose_csv)
        self._path_row(frame, 5, "결과 폴더", self.output_dir, self._choose_output)

        button_row = ttk.Frame(frame)
        button_row.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(16, 8))

        ttk.Button(button_row, text="샘플 CSV 만들기", command=lambda: self._load_sample(open_after=True)).grid(
            row=0, column=0, padx=(0, 8)
        )
        ttk.Button(button_row, text="패킷 생성", command=self._compile).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(button_row, text="결과 폴더 열기", command=self._open_output).grid(row=0, column=2)

        status_label = ttk.Label(frame, textvariable=self.status)
        status_label.grid(row=7, column=0, columnspan=3, sticky="w", pady=(8, 4))

        self.log = tk.Text(frame, height=12, wrap="word")
        self.log.grid(row=8, column=0, columnspan=3, sticky="nsew", pady=(4, 0))
        self.log.insert(
            "end",
            "1. 업무 유형을 선택합니다.\n"
            "2. 직접 내려받은 CSV를 선택하거나 샘플 CSV를 만듭니다.\n"
            "3. 결과 폴더를 확인하고 패킷 생성을 누릅니다.\n\n"
            "내 CSV를 사용할 때는 샘플 CSV의 헤더명과 같은 컬럼명을 사용해야 합니다.\n"
            "입력 CSV는 UTF-8, UTF-8 BOM, CP949, EUC-KR을 순서대로 인식합니다.\n",
        )
        self.log.configure(state="disabled")

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(8, weight=1)

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
        ttk.Button(parent, text="찾기", command=command).grid(row=row, column=2, sticky="e", pady=5)

    def _current_preset(self) -> WorkflowPreset:
        return self.preset_by_label.get(self.selected_preset.get(), default_preset())

    def _preset_changed(self, _: object = None) -> None:
        preset = self._current_preset()
        self.preset_description.set(preset.description)
        self._load_sample(open_after=False)

    def _sample_dir(self, preset: WorkflowPreset) -> Path:
        return default_output_dir() / "samples" / preset.slug

    def _result_dir(self, preset: WorkflowPreset) -> Path:
        return default_output_dir() / "results" / preset.slug

    def _load_sample(self, *, open_after: bool) -> None:
        preset = self._current_preset()
        files = write_preset_files(preset.slug, self._sample_dir(preset))
        self.input_csv.set(str(files["csv"]))
        self.output_dir.set(str(self._result_dir(preset)))
        self._write_log(f"'{preset.label}' 샘플 CSV를 준비했습니다: {files['csv']}\n")
        if open_after:
            open_folder(files["csv"].parent)

    def _choose_csv(self) -> None:
        path = filedialog.askopenfilename(
            title="CSV 파일 선택",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.input_csv.set(path)

    def _choose_output(self) -> None:
        path = filedialog.askdirectory(title="결과 폴더 선택")
        if path:
            self.output_dir.set(path)

    def _compile(self) -> None:
        preset = self._current_preset()
        input_csv = Path(self.input_csv.get()).expanduser()
        output_dir = Path(self.output_dir.get()).expanduser()

        if not input_csv.exists():
            messagebox.showerror("CSV 파일 없음", f"CSV 파일이 없습니다:\n{input_csv}")
            return

        try:
            result = compile_packets_from_config(
                input_csv=input_csv,
                config=preset.config,
                output_dir=output_dir,
                config_source=f"preset:{preset.slug}",
            )
        except Exception as exc:  # pragma: no cover - GUI error boundary
            self.status.set("생성 실패")
            self._write_log(f"\n생성 실패:\n{exc}\n")
            messagebox.showerror("생성 실패", str(exc))
            return

        lines = [
            "",
            "패킷 생성 완료",
            f"업무 유형: {preset.label}",
            f"읽은 행: {result.rows_seen}",
            f"생성된 패킷: {result.packets_created}",
            f"건너뛴 행: {result.skipped_rows}",
            f"결과 폴더: {output_dir}",
        ]
        if result.warnings:
            lines.append("주의:")
            lines.extend(f"- {warning}" for warning in result.warnings)
        self.status.set(f"{result.packets_created}개 패킷 생성됨")
        self._write_log("\n".join(lines) + "\n")
        messagebox.showinfo("FormOps Kit", f"{result.packets_created}개 패킷을 생성했습니다.")

    def _open_output(self) -> None:
        try:
            open_folder(Path(self.output_dir.get()).expanduser())
        except Exception as exc:  # pragma: no cover - platform shell boundary
            messagebox.showerror("폴더 열기 실패", str(exc))

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
