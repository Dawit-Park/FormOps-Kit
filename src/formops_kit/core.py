from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from string import Formatter
from typing import Any, Dict, Iterable, List, Mapping, Optional


class MissingValueDict(dict):
    """A format_map dictionary that renders missing values as empty strings."""

    def __missing__(self, key: str) -> str:
        return ""


@dataclass
class CompileResult:
    rows_seen: int
    packets_created: int
    skipped_rows: int
    warnings: List[str]


def load_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        config = json.load(f)
    if "templates" not in config or not isinstance(config["templates"], dict):
        raise ValueError("Config must include a 'templates' object.")
    return config


def load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV file has no header row.")
        return [{k: (v or "") for k, v in row.items()} for row in reader]


def render_template(template: str, row: Mapping[str, str]) -> str:
    values = MissingValueDict({k: str(v) for k, v in row.items()})
    return template.format_map(values)


def find_template_fields(template: str) -> List[str]:
    fields: List[str] = []
    formatter = Formatter()
    for _, field_name, _, _ in formatter.parse(template):
        if field_name:
            fields.append(field_name)
    return fields


def slugify(value: str, fallback: str = "packet") -> str:
    value = value.strip()
    value = re.sub(r"[\\/:*?\"<>|]+", "-", value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-._")
    return value[:80] or fallback


def row_is_complete(row: Mapping[str, str], required_fields: Iterable[str]) -> bool:
    return all(str(row.get(field, "")).strip() for field in required_fields)


def parse_datetime(date_value: str, time_value: str = "") -> Optional[datetime]:
    date_value = (date_value or "").strip()
    time_value = (time_value or "").strip()
    if not date_value:
        return None

    candidates = []
    if time_value:
        candidates.extend([
            (f"{date_value} {time_value}", "%Y-%m-%d %H:%M"),
            (f"{date_value} {time_value}", "%Y/%m/%d %H:%M"),
            (f"{date_value} {time_value}", "%Y.%m.%d %H:%M"),
            (f"{date_value} {time_value}", "%m/%d/%Y %H:%M"),
        ])
    candidates.extend([
        (date_value, "%Y-%m-%d"),
        (date_value, "%Y/%m/%d"),
        (date_value, "%Y.%m.%d"),
        (date_value, "%m/%d/%Y"),
    ])

    for value, fmt in candidates:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def make_ics(
    *,
    title: str,
    start: datetime,
    duration_minutes: int = 30,
    description: str = "",
) -> str:
    end = start + timedelta(minutes=duration_minutes)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    uid_seed = f"{title}|{start.isoformat()}|{duration_minutes}|{description}"
    uid_hash = hashlib.sha1(uid_seed.encode("utf-8")).hexdigest()[:16]
    uid = f"formops-{start.strftime('%Y%m%dT%H%M%S')}-{uid_hash}@local"

    def escape(text: str) -> str:
        return (
            text.replace("\\", "\\\\")
            .replace(";", "\\;")
            .replace(",", "\\,")
            .replace("\n", "\\n")
        )

    return "\n".join([
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//FormOps Kit//EN",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{stamp}",
        f"DTSTART:{start.strftime('%Y%m%dT%H%M%S')}",
        f"DTEND:{end.strftime('%Y%m%dT%H%M%S')}",
        f"SUMMARY:{escape(title)}",
        f"DESCRIPTION:{escape(description)}",
        "END:VEVENT",
        "END:VCALENDAR",
        "",
    ])


def compile_packets(input_csv: Path, config_path: Path, output_dir: Path) -> CompileResult:
    config = load_config(config_path)
    rows = load_csv(input_csv)

    workflow_name = config.get("workflow_name", "FormOps Workflow")
    folder_template = config.get("folder_name_template", "{Name}")
    required_fields = config.get("required_fields", [])
    templates = config["templates"]
    calendar_config = config.get("calendar", {})

    output_dir.mkdir(parents=True, exist_ok=True)
    warnings: List[str] = []
    packets_created = 0
    skipped_rows = 0

    for index, row in enumerate(rows, start=1):
        if not row_is_complete(row, required_fields):
            skipped_rows += 1
            warnings.append(f"Row {index} skipped: missing required fields {required_fields}.")
            continue

        folder_name = slugify(render_template(folder_template, row), fallback=f"packet-{index:03d}")
        packet_dir = output_dir / f"{index:03d}-{folder_name}"
        packet_dir.mkdir(parents=True, exist_ok=True)

        for file_name, template in templates.items():
            safe_file_name = slugify(file_name, fallback="output.md")
            if "." not in safe_file_name and "." in file_name:
                safe_file_name = file_name
            output_text = render_template(template, row)
            (packet_dir / safe_file_name).write_text(output_text, encoding="utf-8")

        if calendar_config.get("enabled"):
            date_field = calendar_config.get("date_field", "")
            time_field = calendar_config.get("time_field", "")
            start = parse_datetime(row.get(date_field, ""), row.get(time_field, ""))
            if start:
                title = render_template(calendar_config.get("title_template", workflow_name), row)
                description = render_template(calendar_config.get("description_template", ""), row)
                duration = int(calendar_config.get("duration_minutes", 30))
                (packet_dir / "calendar.ics").write_text(
                    make_ics(title=title, start=start, duration_minutes=duration, description=description),
                    encoding="utf-8",
                )
            else:
                warnings.append(f"Row {index}: calendar enabled but date/time could not be parsed.")

        packets_created += 1

    summary = {
        "workflow_name": workflow_name,
        "input_csv": str(input_csv),
        "config": str(config_path),
        "rows_seen": len(rows),
        "packets_created": packets_created,
        "skipped_rows": skipped_rows,
        "warnings": warnings,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    return CompileResult(
        rows_seen=len(rows),
        packets_created=packets_created,
        skipped_rows=skipped_rows,
        warnings=warnings,
    )
