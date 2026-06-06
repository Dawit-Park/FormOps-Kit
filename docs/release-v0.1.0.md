# FormOps Kit v0.1.0 Release Notes

## Summary

FormOps Kit v0.1.0 turns form response CSV files into local operation packets. It is intended for small teams, solo operators, educators, and community managers who collect requests through forms but still handle follow-up manually.

## Included

- CSV input from form or sheet exports
- Config-driven template rendering
- Per-response output folders
- Markdown task checklist generation
- Email draft generation
- Drive folder plan generation
- Calendar `.ics` generation
- `summary.json` run report
- Required field checks with warnings
- Multiple fictional example workflows
- Basic local GUI for choosing CSV, config, and output folder
- Windows-friendly `formops-gui.pyw` launcher
- GitHub Actions workflow for building a Windows `FormOpsKit.exe` artifact
- Manual GitHub Release publishing workflow
- CI workflow for Python 3.9 through 3.12

## Privacy

The default v0.1.0 workflow is local-first. It does not send CSV data to Google, OpenAI, or any hosted backend. All committed example names, companies, emails, amounts, dates, invoice links, and messages are fictional sample data.

## Known Limitations

- No direct Google Forms or Google Sheets API connection yet
- No Gmail draft API connection yet
- No automatic Google Drive folder creation yet
- No automatic Google Calendar event creation yet
- No OpenAI-powered classification or drafting yet
- Direct double-click from source requires Python with `tkinter`
- The Windows executable is built as a workflow artifact; no formal installer is included yet

## Publishing

Maintainers can publish this release from GitHub Actions:

1. Open **Actions**.
2. Select **Publish v0.1 Release**.
3. Run the workflow with tag `v0.1.0`.

The workflow builds `FormOpsKit.exe` and attaches it to the GitHub Release.

## Verification Commands

```bash
python -m compileall -q src tests
python -m formops_kit compile --input examples/responses.csv --config examples/config.json --output outbox/quickstart
python -m formops_kit compile --input examples/course-intake/responses.csv --config examples/course-intake/config.json --output outbox/course-intake
python -m formops_kit compile --input examples/client-consultation/responses.csv --config examples/client-consultation/config.json --output outbox/client-consultation
python -m formops_kit compile --input examples/affiliate-settlement-request/responses.csv --config examples/affiliate-settlement-request/config.json --output outbox/affiliate-settlement-request
```

Install test dependencies before running the full test suite:

```bash
pip install -e ".[dev]"
pytest
```
