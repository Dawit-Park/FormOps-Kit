from pathlib import Path

from datetime import datetime

from formops_kit.core import (
    compile_packets,
    compile_packets_from_config,
    load_csv,
    make_ics,
    parse_datetime,
    render_template,
    slugify,
)
from formops_kit.presets import get_preset


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


def test_load_csv_reads_korean_excel_cp949(tmp_path: Path):
    csv_path = tmp_path / "responses.csv"
    csv_path.write_bytes("이름,이메일\n샘플 사용자,user@example.com\n".encode("cp949"))

    rows = load_csv(csv_path)

    assert rows == [{"이름": "샘플 사용자", "이메일": "user@example.com"}]


def test_parse_datetime_accepts_korean_date_and_time():
    assert parse_datetime("2026년 6월 12일", "오후 2시").strftime("%Y-%m-%d %H:%M") == "2026-06-12 14:00"
    assert parse_datetime("2026.06.13", "오전 10:30").strftime("%Y-%m-%d %H:%M") == "2026-06-13 10:30"
    assert parse_datetime("2026년 6월 14일 오후 3시 30분").strftime("%Y-%m-%d %H:%M") == "2026-06-14 15:30"


def test_compile_packets_from_korean_preset(tmp_path: Path):
    preset = get_preset("kr-course-inquiry")
    csv_path = tmp_path / "responses.csv"
    output_dir = tmp_path / "outbox"
    csv_path.write_text(preset.sample_csv, encoding="utf-8-sig")

    result = compile_packets_from_config(
        input_csv=csv_path,
        config=preset.config,
        output_dir=output_dir,
        config_source=f"preset:{preset.slug}",
    )

    assert result.rows_seen == 2
    assert result.packets_created == 2
    packet_dirs = [p for p in output_dir.iterdir() if p.is_dir()]
    assert len(packet_dirs) == 2
    assert (packet_dirs[0] / "처리체크리스트.md").exists()
    assert (packet_dirs[0] / "답장초안.md").exists()
    assert (packet_dirs[0] / "폴더계획.md").exists()
    assert (packet_dirs[0] / "calendar.ics").exists()


def test_make_ics_uses_stable_uid_for_same_event():
    start = datetime(2026, 6, 12, 14, 0)
    first = make_ics(title="Follow-up", start=start, description="Same request")
    second = make_ics(title="Follow-up", start=start, description="Same request")

    first_uid = next(line for line in first.splitlines() if line.startswith("UID:"))
    second_uid = next(line for line in second.splitlines() if line.startswith("UID:"))

    assert first_uid == second_uid
