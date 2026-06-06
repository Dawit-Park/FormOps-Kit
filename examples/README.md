# FormOps Kit Examples

Each example contains a `responses.csv` file and a matching `config.json`.

## Sample Data Notice

All names, companies, emails, amounts, dates, invoice links, and messages in this folder are fictional sample data. They are included only to demonstrate how FormOps Kit works. Do not use real customer, student, client, partner, or internal business data in public examples.

## 샘플 데이터 안내

이 폴더의 이름, 회사명, 이메일, 금액, 날짜, 인보이스 링크, 메시지는 모두 사용 예시를 위한 가상 데이터입니다. 실제 고객, 수강생, 거래처, 파트너, 내부 업무 데이터를 공개 예시에 넣지 마세요.

Run any example from the project root after installing the package with `pip install -e .`.

```bash
formops compile --input examples/course-intake/responses.csv --config examples/course-intake/config.json --output outbox/course-intake
formops compile --input examples/client-consultation/responses.csv --config examples/client-consultation/config.json --output outbox/client-consultation
formops compile --input examples/affiliate-settlement-request/responses.csv --config examples/affiliate-settlement-request/config.json --output outbox/affiliate-settlement-request
```

The root `examples/config.json` and `examples/responses.csv` files are kept as the smallest quick-start workflow.
