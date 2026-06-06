from pathlib import Path

from datetime import datetime

from formops_kit.core import compile_packets, make_ics, render_template, slugify


def test_render_template_replaces_csv_columns():
    assert render_template("Hi {Name}", {"Name": "Mina"}) == "Hi Mina"


def test_slugify_removes_unsafe_characters():
    assert slugify('A/B:C*D?') == "A-B-C-D"


def test_compile_packets(tmp_path: Path):
    csv_path = tmp_path / "responses.csv"
    config_path = tmp_path / "config.json"
    output_dir = tmp_path / "outbox"

    csv_path.write_text(
        "Name,Email,Request Type,Preferred Date,Preferred Time,Message\n"
        "Sample Learner A,learner-a@example.com,Course,2026-06-12,14:00,Hello\n",
        encoding="utf-8",
    )
    config_path.write_text(
        """{
          "workflow_name": "Test",
          "folder_name_template": "{Name}",
          "required_fields": ["Name", "Email"],
          "templates": {"task.md": "Task for {Name}"},
          "calendar": {
            "enabled": true,
            "date_field": "Preferred Date",
            "time_field": "Preferred Time",
            "title_template": "Meet {Name}"
          }
        }""",
        encoding="utf-8",
    )

    result = compile_packets(csv_path, config_path, output_dir)

    assert result.rows_seen == 1
    assert result.packets_created == 1
    packet_dirs = [p for p in output_dir.iterdir() if p.is_dir()]
    assert len(packet_dirs) == 1
    assert (packet_dirs[0] / "task.md").exists()
    assert (packet_dirs[0] / "calendar.ics").exists()


def test_compile_packets_skips_missing_required_fields(tmp_path: Path):
    csv_path = tmp_path / "responses.csv"
    config_path = tmp_path / "config.json"
    output_dir = tmp_path / "outbox"

    csv_path.write_text(
        "Name,Email,Request Type\n"
        "Sample Learner A,,Course\n",
        encoding="utf-8",
    )
    config_path.write_text(
        """{
          "workflow_name": "Test",
          "folder_name_template": "{Name}",
          "required_fields": ["Name", "Email"],
          "templates": {"task.md": "Task for {Name}"}
        }""",
        encoding="utf-8",
    )

    result = compile_packets(csv_path, config_path, output_dir)

    assert result.rows_seen == 1
    assert result.packets_created == 0
    assert result.skipped_rows == 1
    assert result.warnings


def test_make_ics_uses_stable_uid_for_same_event():
    start = datetime(2026, 6, 12, 14, 0)
    first = make_ics(title="Follow-up", start=start, description="Same request")
    second = make_ics(title="Follow-up", start=start, description="Same request")

    first_uid = next(line for line in first.splitlines() if line.startswith("UID:"))
    second_uid = next(line for line in second.splitlines() if line.startswith("UID:"))

    assert first_uid == second_uid
