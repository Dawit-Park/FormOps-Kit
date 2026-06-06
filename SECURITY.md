# Security Policy

FormOps Kit is local-first by default. It should not send form data to external services unless the user explicitly enables a connector.

## Reporting a vulnerability

Please open a private security advisory if available, or contact the maintainer directly.

## Connector principles

Future API connectors should follow these principles:

- Use the least privileged OAuth scopes possible
- Do not log access tokens or private form responses
- Keep external API calls opt-in
- Document exactly what data is sent and where
- Provide a dry-run mode whenever possible
