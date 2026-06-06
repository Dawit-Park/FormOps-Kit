# FormOps Kit

Turn Google Forms / Google Sheets responses into ready-to-use operation packets: task checklists, email drafts, calendar files, and Drive folder plans.

FormOps Kit is a local-first Python CLI for small teams, solo operators, educators, community managers, and non-developers who collect requests through forms but still handle follow-up manually.

## 한국어 소개

FormOps Kit은 Google Forms나 Google Sheets에서 내려받은 신청, 상담, 요청 CSV를 바로 처리 가능한 업무 패킷으로 바꿔주는 오픈소스 CLI입니다.

예를 들어 강의 문의나 고객 상담 신청 CSV를 넣으면 각 응답자별로 다음 파일을 생성합니다.

- `task.md`: 후속 처리 체크리스트
- `email-draft.md`: Gmail 등에 붙여 넣을 수 있는 답장 초안
- `drive-folder-plan.md`: Google Drive 폴더 구성안
- `calendar.ics`: 캘린더에 가져올 수 있는 일정 파일

v0.1은 Google API나 OpenAI API 없이 로컬 CSV만 처리합니다. 민감한 폼 응답 데이터는 기본 동작에서 외부 서비스로 전송되지 않습니다.

## Why This Exists

Many small teams already use forms for intake, applications, consultations, classes, surveys, orders, and internal requests. The hard part is not collecting the response. The hard part is turning each response into the next action.

FormOps Kit starts with a plain CSV export and creates repeatable follow-up packets. It is intentionally boring at v0.1: no account setup, no OAuth consent screen, no API key, and no hosted backend.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .

formops compile \
  --input examples/responses.csv \
  --config examples/config.json \
  --output outbox
```

After running the command, open the `outbox/` folder.

You can also create starter example files in another folder:

```bash
formops init --path my-formops-workflow
```

## Click-Only GUI

For non-developers on Windows, FormOps Kit also includes a small local GUI.

If you downloaded the source code, double-click:

```text
formops-gui.pyw
```

The GUI lets you choose:

- a CSV input file
- a `config.json` file
- an output folder

Then click **Compile packets**. The same local compiler is used under the hood, so the GUI does not send form data to Google, OpenAI, or any hosted backend.

If you installed the package in a Python environment, you can also start the GUI with:

```bash
formops-gui
```

Current GUI limitation: it still requires Python with `tkinter` installed. A packaged one-file app or installer is not included yet.

## Example Workflows

The repository includes several sample workflows that can be run as-is:

```bash
formops compile \
  --input examples/course-intake/responses.csv \
  --config examples/course-intake/config.json \
  --output outbox/course-intake

formops compile \
  --input examples/client-consultation/responses.csv \
  --config examples/client-consultation/config.json \
  --output outbox/client-consultation

formops compile \
  --input examples/affiliate-settlement-request/responses.csv \
  --config examples/affiliate-settlement-request/config.json \
  --output outbox/affiliate-settlement-request
```

## Configuration

Edit a `config.json` file to map form columns into output templates.

```json
{
  "workflow_name": "Consultation Intake",
  "folder_name_template": "{Name}-{Request Type}",
  "required_fields": ["Name", "Email"],
  "templates": {
    "task.md": "# Follow-up for {Name}\n\n- [ ] Reply to {Email}\n- [ ] Review request: {Request Type}\n",
    "email-draft.md": "Subject: We received your request\n\nHi {Name},\n\nThanks for your message. We will review it and follow up soon.\n",
    "drive-folder-plan.md": "# Drive folder plan\n\nFolder: {Name} - {Request Type}\n"
  }
}
```

Column names in braces, such as `{Name}` or `{Request Type}`, are replaced with values from the CSV file.

## Calendar Files

If the config includes a `calendar` block, FormOps Kit creates a `calendar.ics` file for each response with a valid date.

```json
{
  "calendar": {
    "enabled": true,
    "date_field": "Preferred Date",
    "time_field": "Preferred Time",
    "duration_minutes": 30,
    "title_template": "Follow-up: {Name}",
    "description_template": "Email: {Email}\nMessage: {Message}"
  }
}
```

Supported date formats include `YYYY-MM-DD`, `YYYY/MM/DD`, `YYYY.MM.DD`, and `MM/DD/YYYY`. Times use `HH:MM`.

## Current Scope

FormOps Kit v0.1 focuses on local CSV-to-files workflows:

- CSV input
- Markdown packet generation
- Required field checks
- Per-response output folders
- Calendar `.ics` generation
- Basic click-only GUI for local compilation
- Summary report in `summary.json`
- Example workflows for real operating patterns

## Roadmap

- [x] CSV input
- [x] Markdown packet generation
- [x] Basic calendar `.ics` generation
- [x] Multiple example workflows
- [x] Basic click-only GUI
- [ ] Google Sheets connector
- [ ] Gmail draft connector
- [ ] Google Calendar connector
- [ ] Google Drive folder creator
- [ ] Trello / Asana task export
- [ ] Optional OpenAI-powered classification and draft generation
- [ ] Packaged desktop app / installer for non-Python users

## Privacy and Safety

FormOps Kit is local-first. In the default workflow, your CSV is processed on your machine and no data is sent to OpenAI, Google, or any other API.

Future connectors should be explicit opt-in features with clear scopes, dry-run behavior where possible, and documentation that explains exactly what data is sent and where.

## Development

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

Run the GUI from a development checkout:

```bash
python formops-gui.pyw
```

## Maintainer Notes

This project is intended to grow through practical workflows, not inflated usage claims. Useful contributions include new example configs, real-world template improvements, tests for messy CSV exports, and connector design proposals.

## License

MIT License. See [LICENSE](LICENSE).
