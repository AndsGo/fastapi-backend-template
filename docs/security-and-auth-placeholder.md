# Security And Auth Placeholder

Authentication and authorization are intentionally placeholders in this template.

Current behavior:

- `get_current_user()` reads optional actor headers.
- `require_permission()` does not enforce permissions yet.
- API code can depend on these placeholders without choosing a final auth provider.

Future projects should replace this with their chosen SSO, OAuth2, OIDC, API key, or RBAC design.

Rules:

- Do not hard-code credentials.
- Do not store real secrets in `.env.example`, logs, tests, or docs.
- Keep credentials in environment variables or a secret manager.
