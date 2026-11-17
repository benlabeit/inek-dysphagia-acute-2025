# Dysphagia in acute neurological complex treatment: InEK 2025

This private project contains an English manuscript draft and reproducible aggregate analyses of coded dysphagia in acute neurological complex-treatment hospital episodes in Germany. The analysis uses **Unterjährige Datenlieferung DRG Januar bis Dezember 2025**, whose documented delivery snapshot is 16 January 2026. It is a provisional reporting snapshot, not verified final population completeness.

[Project repository](https://github.com/benlabeit/inek-dysphagia-acute-2025) · [Companion early-rehabilitation manuscript](https://github.com/benlabeit/inek-dysphagia-rehabilitation-2025)

## Manuscript and scientific status

`manuscript_acute.md` is the English source draft. `Manuscript_Acute_Dysphagia_2025.docx` is the editable Word version, and `Manuscript_Acute_Dysphagia_2025.pdf` is the fixed-layout reading copy. These manuscript versions require author review of interpretation, authorship, affiliations, declarations, journal requirements, and limitations before submission. `acute_literature_final.json` records the literature assessment.

The unit is a hospital DRG episode, not a unique person. Dysphagia means a selected R13.0/R13.1/R13.9 **secondary diagnosis**. The comparator lacks these selected secondary codes; a principal dysphagia diagnosis or uncoded dysphagia is not excluded. The OPS cohort is a care-pathway cohort and includes indications beyond confirmed stroke. Additional analyses were selected after reviewing the original presentation and are exploratory.

Root CSV files are curated output snapshots. Raw workbooks, full parsed code tables, and generated result JSON are excluded from this repository. It contains no rehabilitation-specific inputs or analyses. The separate companion cohort can share hospital episodes or patients with this cohort; its totals must not be added as independent patients or combined attributable burden.

## Reproduce

Tested with Python 3.12.14, openpyxl 3.1.5, and et_xmlfile 2.0.0. The latter is the installed dependency of openpyxl; all other analysis imports are from Python's standard library.

```sh
python -m pip install -r requirements.txt
python run_all.py --check-inputs
python run_all.py
```

Place these six unchanged original exports in `raw/` beside the scripts:

| Filename | Cases |
|---|---:|
| acute_all_2025.xlsx | 279277 |
| acute_dys_2025.xlsx | 33643 |
| acute_all_death_2025.xlsx | 12749 |
| acute_dys_death_2025.xlsx | 5003 |
| acute_all_pneumonia_2025.xlsx | 10901 |
| acute_dys_pneumonia_2025.xlsx | 3875 |

`query_manifest.json` records the exact filters from `Info!A2`, delivery from `Info!A5`, case counts from `Info!B8`, original SHA-256 hashes, and SD diagnostics. Obtain exports from the [InEK DatenBrowser](https://datenbrowser.inek.org/) using those exact selections and delivery. Within a field codes form an OR union; distinct fields are combined with AND. Keep `Nebendiagnosen` and `weitere Nebendiagnosen` separate in pneumonia queries.

Default validation requires original bytes. For an independently downloaded workbook with different container metadata, `--allow-hash-mismatch` explicitly permits changed bytes while still requiring the exact stored selection string, delivery, and N. This is not a substitute for reviewing data changes. New deliveries or cohorts require a revised manifest and scientific review.

The runner works when invoked from another directory, validates all six inputs before analysis, sets subprocess working directories, and stops on failure. It never edits source workbooks.

## Pipeline and outputs

1. `analyze_acute_exports.py` parses exports and calculates the base comparison and within-DRG standardization; writes `results/acute_reanalysis.json`.
2. `analyze_acute_extensions.py` adds mortality, exact pneumonia unions, age-standardized mortality, and survivor analyses from the six exports; writes `results/acute_extensions.json`.
3. `export_summary_tables.py` creates `results/key_results.csv`, `results/drg_standardization.csv`, and `results/sd_convention_audit.csv` using only acute results.

`parsed/` receives local full tables; `results/` also receives execution logs. Both directories are Git-ignored. To refresh curated snapshots, review and copy only the three CSVs to the root. Rates are proportions. Blank event-count fields for standardized risks mean that no single binomial count represents the weighted rate, not that there were zero events.

`methods.md` documents moment reconstruction, separate Info/DRG SD conventions, suppression, standardization, clinical-code corrections, and outstanding queries. Confidence intervals are model-based and do not cover coding or selection bias. DRG and age standardization do not establish a causal dysphagia effect; associated bed-days are not proven avoidable days.

No software or data license has yet been selected. InEK access and reuse conditions continue to apply to original exports.
