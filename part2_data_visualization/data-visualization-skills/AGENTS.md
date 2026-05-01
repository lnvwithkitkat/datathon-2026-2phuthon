# Data Visualization Kit Rules

## Git Protection

- Never stage, commit, or push changes under `docs/`.
- Never stage, commit, or push changes under `plans/`.
- `projects/README.md` stays core-kit owned.
- Project-specific user content belongs under `projects/` and may be committed when explicitly requested.

## Enforcement

- Git hooks live under `.githooks/`.
- Install or refresh them with `npm run kit:hooks:install`.
- The hooks block commits and pushes that include `docs/` or `plans/` paths.
