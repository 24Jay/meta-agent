# Security Policy

## Do Not Commit Sensitive Data

Do not commit:

- API keys, tokens, passwords, private keys, credentials, or cookies.
- Customer data, user chat logs, production run logs, device identifiers, or internal system paths.
- Private repository URLs, internal dashboards, private wiki links, or confidential business data.
- Raw memory files from private projects.

## Agent Safety Principles

meta-agent separates evidence and risk:

- `evidence_level` describes how strong the support for a conclusion is.
- `risk_level` describes how risky an action is.

Any action affecting production systems, external communication, user data, infrastructure, or real-world devices must require human approval.

## Reporting Security Issues

Please report security issues privately through GitHub Security Advisories when available. If advisories are not enabled for the repository, open a minimal public issue asking for a private disclosure channel without including exploit details.

Do not disclose vulnerabilities publicly before maintainers have had time to respond.
