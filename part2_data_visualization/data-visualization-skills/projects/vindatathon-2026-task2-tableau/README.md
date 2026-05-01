# VinDatathon 2026 Task 2 Dashboard Analysis

Part 2-only dashboard analysis package for the VinDatathon 2026 e-commerce fashion dataset. The current submission-ready path is a reproducible, LaTeX-ready rendered figure pack plus a manual Power BI rebuild guide.

## Main Deliverables

- Final rendered figures: `docs/assets/figures/latex/`
- Power BI rebuild guide: `docs/powerbi-rebuild-guide.md`
- GitHub submission guide: `docs/github-submission.md`
- File inventory: `docs/file-inventory.md`
- Validation report: `docs/data-preparation-validation.md`
- Dashboard story: `docs/dashboard-story.md`

## Reproduce Data And Figures

```powershell
& 'C:\Users\Admn\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\scripts\prepare_tableau_data.py
& 'C:\Users\Admn\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\scripts\generate_latex_figure_pack.py
```

Prepared analytical extracts are in:

```text
docs/assets/exports/tableau/
```

Final LaTeX-ready outputs are in:

```text
docs/assets/figures/latex/
```

## GitHub Notes

The project-local `.gitignore` excludes oversized generated extracts and BI binary files. In particular, do not commit these without Git LFS or GitHub Release assets:

- `docs/assets/exports/tableau/orders_enriched.csv`
- `docs/assets/exports/tableau/order_items_enriched.csv`
- `docs/assets/workbook/VinDatathon_Task2_Tableau_Fileout_Package.zip`
- `.pbix`, `.twbx`, and similar BI binaries

Follow `docs/github-submission.md` before staging files.
