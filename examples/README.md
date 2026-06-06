# FormOps Kit Examples

Each example contains a `responses.csv` file and a matching `config.json`.

Run any example from the project root after installing the package with `pip install -e .`.

```bash
formops compile --input examples/course-intake/responses.csv --config examples/course-intake/config.json --output outbox/course-intake
formops compile --input examples/client-consultation/responses.csv --config examples/client-consultation/config.json --output outbox/client-consultation
formops compile --input examples/affiliate-settlement-request/responses.csv --config examples/affiliate-settlement-request/config.json --output outbox/affiliate-settlement-request
```

The root `examples/config.json` and `examples/responses.csv` files are kept as the smallest quick-start workflow.
