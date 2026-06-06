# Contributing

Thanks for helping improve FormOps Kit.

## Good first contributions

- Add a new example workflow under `examples/`
- Improve README setup instructions
- Add tests for date/time formats
- Propose connector specs for Google Sheets, Gmail, Calendar, Drive, Trello, Asana, or Notion
- Improve privacy and safety documentation

## Local development

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

## Pull request checklist

- [ ] The change is documented
- [ ] Tests pass locally
- [ ] No private or sensitive data is included
- [ ] New connectors are opt-in and document permissions clearly
