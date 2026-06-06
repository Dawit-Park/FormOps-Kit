from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from .core import compile_packets


EXAMPLE_CONFIG = """{
  "workflow_name": "Consultation Intake",
  "folder_name_template": "{Name}-{Request Type}",
  "required_fields": ["Name", "Email"],
  "templates": {
    "task.md": "# Follow-up for {Name}\n\n- [ ] Reply to {Email}\n- [ ] Review request type: {Request Type}\n- [ ] Check preferred date: {Preferred Date} {Preferred Time}\n- [ ] Create Drive folder\n\n## Notes\n{Message}\n",
    "email-draft.md": "Subject: We received your request\n\nHi {Name},\n\nThanks for your message about {Request Type}. We received it and will follow up soon.\n\nBest,\nYour team\n",
    "drive-folder-plan.md": "# Drive folder plan\n\nFolder name: {Name} - {Request Type}\n\nSuggested files:\n- intake.md\n- notes.md\n- attachments/\n"
  },
  "calendar": {
    "enabled": true,
    "date_field": "Preferred Date",
    "time_field": "Preferred Time",
    "duration_minutes": 30,
    "title_template": "Follow-up: {Name} / {Request Type}",
    "description_template": "Email: {Email}\nMessage: {Message}"
  }
}
"""

EXAMPLE_CSV = """Timestamp,Name,Email,Request Type,Preferred Date,Preferred Time,Message
2026-06-06 09:00,Kim Mina,mina@example.com,Course inquiry,2026-06-12,14:00,I want to ask about the AI productivity course.
2026-06-06 10:15,Park Joon,joon@example.com,Automation help,2026-06-13,10:30,Can you help automate our Google Forms workflow?
"""


def cmd_init(args: argparse.Namespace) -> None:
    target = Path(args.path)
    target.mkdir(parents=True, exist_ok=True)
    examples = target / "examples"
    examples.mkdir(exist_ok=True)
    (examples / "config.json").write_text(EXAMPLE_CONFIG, encoding="utf-8")
    (examples / "responses.csv").write_text(EXAMPLE_CSV, encoding="utf-8")
    print(f"Created example files under {examples}")


def cmd_compile(args: argparse.Namespace) -> None:
    result = compile_packets(
        input_csv=Path(args.input),
        config_path=Path(args.config),
        output_dir=Path(args.output),
    )
    print(f"Rows seen: {result.rows_seen}")
    print(f"Packets created: {result.packets_created}")
    print(f"Skipped rows: {result.skipped_rows}")
    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"- {warning}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="formops",
        description="Turn form responses into operation packets.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create example config and CSV files.")
    init_parser.add_argument("--path", default=".", help="Target project path. Default: current directory.")
    init_parser.set_defaults(func=cmd_init)

    compile_parser = subparsers.add_parser("compile", help="Compile CSV responses into operation packets.")
    compile_parser.add_argument("--input", required=True, help="Path to CSV export from a form or sheet.")
    compile_parser.add_argument("--config", required=True, help="Path to config JSON.")
    compile_parser.add_argument("--output", default="outbox", help="Output folder. Default: outbox.")
    compile_parser.set_defaults(func=cmd_compile)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
