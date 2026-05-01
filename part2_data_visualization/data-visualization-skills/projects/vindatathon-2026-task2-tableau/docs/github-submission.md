# GitHub Submission Guide

This project is now organized for a manual GitHub submission. The recommended GitHub commit should include the analysis code, documentation, small summary extracts, Power BI rebuild instructions, and final rendered figures. It should not include oversized generated CSVs or BI binary packages unless you intentionally use Git LFS.

## Recommended Commit Scope

Commit this project folder:

```text
projects/vindatathon-2026-task2-tableau/
```

Do not stage the repository-level `docs/` or `plans/` folders. This kit protects those paths, and this project keeps its own documentation under:

```text
projects/vindatathon-2026-task2-tableau/docs/
```

## Commit-Safe Files

These are safe and useful to publish:

- `README.md`
- `.gitignore`
- `scripts/prepare_tableau_data.py`
- `scripts/build_tableau_fileout.py`
- `scripts/generate_preview_exports.py`
- `scripts/generate_latex_figure_pack.py`
- `docs/*.md`
- `docs/assets/figures/latex/*.png`
- `docs/assets/figures/latex/*.pdf`
- `docs/assets/figures/latex/*.tex`
- `docs/assets/figures/latex/figure_manifest.json`
- `docs/assets/figures/latex/VinDatathon_Task2_LaTeX_Figure_Pack.zip`
- `docs/assets/screenshots/*.png`
- `docs/assets/screenshots/*.pdf`
- Small metadata and summary extracts in `docs/assets/exports/tableau/`
- `docs/assets/exports/tableau/orders_enriched_missingness.csv`
- `docs/assets/exports/tableau/order_items_enriched_missingness.csv`
- Workbook build metadata in `docs/assets/workbook/`, except ignored large binaries.

## Files Ignored By Default

The project-local `.gitignore` excludes files that are too large or too binary-heavy for normal GitHub commits:

| File | Reason |
|---|---|
| `docs/assets/exports/tableau/orders_enriched.csv` | 280.9 MB generated extract |
| `docs/assets/exports/tableau/order_items_enriched.csv` | 323.1 MB generated extract |
| `docs/assets/workbook/VinDatathon_Task2_Tableau_Fileout_Package.zip` | 141.7 MB local Tableau package |
| `docs/assets/powerbi/*.pbix` | Binary report files can become large |
| `docs/assets/powerbi/*.pbit` | Binary template files |
| `docs/assets/workbook/*.twbx` | Binary Tableau workbook packages |

If you need to publish those files, use Git LFS or attach them to a GitHub Release instead of committing them directly.

## Optional Raw Dataset Policy

The original raw CSVs live outside this project:

```text
projects/data/
```

All raw CSVs are under 50 MB each, so GitHub can technically accept them. Only publish them if the dataset license or competition rules allow redistribution. If you do commit them, keep the Part 2 scope clear:

- Use the 13 business CSVs.
- Do not analyze `sample_submission.csv`.
- Do not use unavailable `sales_test.csv`.
- Do not use `baseline.ipynb`.

## Manual Git Steps

From the repository root:

```powershell
git status --short
git add projects/vindatathon-2026-task2-tableau
git status --short
```

Before committing, check that these are not staged:

```text
projects/vindatathon-2026-task2-tableau/docs/assets/exports/tableau/orders_enriched.csv
projects/vindatathon-2026-task2-tableau/docs/assets/exports/tableau/order_items_enriched.csv
projects/vindatathon-2026-task2-tableau/docs/assets/workbook/VinDatathon_Task2_Tableau_Fileout_Package.zip
```

Then commit manually:

```powershell
git commit -m "Add VinDatathon Task 2 dashboard analysis package"
```

## Suggested GitHub README Summary

Use this short description in your GitHub repository or release notes:

```text
VinDatathon 2026 Task 2 dashboard analysis package. Includes validated multi-table EDA extracts, reproducible Python data-preparation/rendering scripts, LaTeX-ready high-resolution dashboard figures, Power BI rebuild guide, data dictionary, validation notes, and CEO-oriented business recommendations. Large generated fact extracts are ignored by default and can be regenerated from the raw CSVs.
```

## Submission Checklist

- [ ] `docs/powerbi-rebuild-guide.md` is present.
- [ ] `docs/file-inventory.md` is present.
- [ ] `docs/assets/figures/latex/` contains 8 final PNGs.
- [ ] `docs/assets/figures/latex/VinDatathon_Task2_LaTeX_Figure_Pack.pdf` is present.
- [ ] `docs/assets/figures/latex/figure_manifest.json` is present.
- [ ] `docs/assets/figures/latex/latex_include_figures.tex` is present.
- [ ] Large ignored generated extracts are not staged.
- [ ] No top-level `docs/` or `plans/` changes are staged.
- [ ] If publishing raw `projects/data/`, redistribution is allowed.
- [ ] If publishing `.pbix` or `.twbx`, use Git LFS or GitHub Release assets.
