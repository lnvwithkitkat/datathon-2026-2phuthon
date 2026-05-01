# Document Management

## Canonical Files

- `../README.md`: GitHub-facing project overview and quick start.
- `project-brief.md`: project context and decisions.
- `project-plan.md`: implementation plan and current constraint.
- `data-preparation.md`: prepared data contract.
- `data-preparation-validation.md`: generated validation checks.
- `orders-enriched-null-policy.md`: explanation of expected sparse event columns in `orders_enriched.csv`.
- `order-items-enriched-null-policy.md`: explanation of expected sparse event columns in `order_items_enriched.csv`.
- `erd.md`: relationship notes for Tableau modeling.
- `visualization.md`: selected Tableau path, dashboard pages, and actions.
- `dashboard-story.md`: narrative and rubric mapping.
- `powerbi-rebuild-guide.md`: manual Power BI rebuild guide using the validated extracts and final figure pack.
- `powerbi-visual-diversity-plan.md`: Power BI chart-type mix and page-level diversity guidance.
- `github-submission.md`: manual GitHub submission checklist and staging guidance.
- `file-inventory.md`: project file inventory, commit-safe assets, ignored large artifacts.
- `submission-manifest.json`: machine-readable commit groups and large-file exclusions.
- `publish.md`: file-out status and remaining blocker.

## Asset Layout

- Prepared CSVs: `docs/assets/exports/tableau/`
- Workbook package and Tableau build assets: `docs/assets/workbook/`
- Screenshots/PDF exports after Tableau activation: `docs/assets/screenshots/`
- LaTeX-ready rendered figure pack: `docs/assets/figures/latex/`
- Future manual Power BI files: `docs/assets/powerbi/`

## GitHub Submission Policy

- Commit project docs, scripts, final figures, and small summary extracts.
- Do not commit generated extracts over 100 MB without Git LFS.
- Do not commit `.pbix`, `.twbx`, or other binary dashboard files unless using Git LFS or GitHub Releases.
- The project-local `.gitignore` excludes the largest generated outputs by default.

## Protection Rule

Do not place project-specific deliverables in top-level `docs/` or `plans/`. This project keeps all documentation and assets inside `projects/vindatathon-2026-task2-tableau/docs/`.
