# FormOps Kit v0.1.1 Release Notes

## Summary

FormOps Kit v0.1.1 improves the first-use experience for Korean Windows users. It adds built-in Korean workflow presets, Korean sample CSV generation, and safer handling for CSV files exported from Korean Excel or Google Sheets.

## Added

- Korean GUI flow based on workflow type selection
- Built-in Korean presets:
  - 강의/교육 문의
  - 고객 상담/프로젝트 문의
  - 파트너 정산 요청
- GUI button for generating sample CSV files for the selected workflow
- CLI preset commands:
  - `formops presets`
  - `formops init --preset kr-course-inquiry`
  - `formops compile --input responses.csv --preset kr-course-inquiry`
- Korean output file names such as `처리체크리스트.md`, `답장초안.md`, and `폴더계획.md`

## Korean CSV Compatibility

- Reads UTF-8, UTF-8 BOM, CP949, and EUC-KR CSV files
- Supports common Korean date/time values:
  - `2026년 6월 12일`
  - `2026.06.12`
  - `오후 2시`
  - `오전 10:30`
  - `2026년 6월 12일 오후 2시 30분`

## Fixed

- Reduced the need for non-developers to edit `config.json` manually
- Kept generated text files in UTF-8
- Preserved the local-first behavior: no Google, OpenAI, or hosted backend calls are made by default

## Known Limitations

- Still no automatic Gmail sending
- Still no automatic Google Drive folder creation
- Still no automatic Google Calendar event creation
- The Windows app is still a portable executable, not a signed installer

## Verification Commands

```bash
python -m compileall -q src tests formops-gui.pyw
python -m formops_kit.cli presets
python -m formops_kit.cli init --path outbox/kr-course-sample --preset kr-course-inquiry
python -m formops_kit.cli compile --input outbox/kr-course-sample/examples/responses.csv --preset kr-course-inquiry --output outbox/kr-course-packets
```

Install test dependencies before running the full test suite:

```bash
pip install -e ".[dev]"
pytest
```
