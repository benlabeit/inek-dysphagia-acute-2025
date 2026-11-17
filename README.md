# Dysphagia in acute neurological complex treatment: InEK 2025

This private project contains an English manuscript draft and reproducible aggregate analyses of coded dysphagia in acute neurological complex-treatment hospital episodes in Germany. The analysis uses **Unterjährige Datenlieferung DRG Januar bis Dezember 2025**, whose documented delivery snapshot is 16 January 2026. It is a provisional reporting snapshot, not verified final population completeness.

[Project repository](https://github.com/benlabeit/inek-dysphagia-acute-2025) · [Companion early-rehabilitation manuscript](https://github.com/benlabeit/inek-dysphagia-rehabilitation-2025)

## Manuscript and scientific status

`manuscript_acute.md` is the English source draft. `Manuscript_Acute_Dysphagia_2025.docx` is the editable Word version, and `Manuscript_Acute_Dysphagia_2025.pdf` is the fixed-layout reading copy. These manuscript versions require author review of interpretation, authorship, affiliations, declarations, journal requirements, and limitations before submission. `acute_literature_final.json` records the literature assessment.

The unit is a hospital DRG episode, not a unique person. Dysphagia means a selected R13.0/R13.1/R13.9 **secondary diagnosis**. The comparator lacks these selected secondary codes; a principal dysphagia diagnosis or uncoded dysphagia is not excluded. The OPS cohort is a care-pathway cohort and includes indications beyond confirmed stroke. Additional analyses were selected after reviewing the original presentation and are exploratory.

Root CSV files are curated output snapshots. Raw workbooks, full parsed code tables, and generated result JSON are excluded from this repository. It contains no rehabilitation-specific inputs or analyses. The separate companion cohort can share hospital episodes or patients with this cohort; its totals must not be added as independent patients or combined attributable burden.

## Severity sensitivity revision of 17 November 2026

Completed additions use the same original exports and do not change the original cohort definition:

- Seven-level PCCL direct standardization: mortality RR **3.20 (3.07-3.33)** and J12-J18 pneumonia RR **2.07 (1.97-2.16)**, with 95% model-based confidence intervals and the pooled cohort PCCL distribution as reference.
- Explicit principal-diagnosis mortality comparisons, including complete I61 and an explicitly restricted I63 set **excluding I63.6**. Suppressed or absent endcode rows are never set to zero.
- All 21 planned U50/U51 categories, kept within five distinct instruments, for mortality and J12-J18 pneumonia. Within Barthel 0-15 (U50.50), mortality RR is **1.08 (1.03-1.15)**. The other categories, unknown rows, coding coverage bounds, and sparse cells are also retained; this example is not the whole sensitivity analysis.

These are separate descriptive standardizations or code-conditioned comparisons. None is admission-NIHSS adjustment, and their attenuation cannot be interpreted as a causal percentage explained. PCCL can include downstream complications. Functional coding is incomplete, may depend on assessment practices, and cannot be aligned precisely with dysphagia or outcome onset. The code-absent complement is not a normal-function group.

The joint age-by-sex-by-principal-diagnosis analysis requires additional exports. A planned query definition and reproducible implementation are included separately; the current original six/seven workbooks do not supply the required cross-classified cells. Until the new files are obtained and validated, it remains **pending**, not an accomplished multivariable adjustment. The exact 24-query plan is `joint_query_plan.json`, with methods in `joint_standardization_methods.md`. The default runner performs an availability check only and creates no joint effect estimates. Once all additional files are obtained, use:

```sh
python run_all.py --joint
```

This validates the original inputs and executes all completed analyses followed by the new joint mortality analysis. A missing joint workbook causes the requested joint run to fail; it never substitutes a zero cell. An isolated check is `python analyze_joint_standardization.py --cohort acute --status-only`. `--check-inputs` applies to the original manifest only; it does not validate the new joint analysis.


### Additional pipeline steps and curated tables

`run_all.py` executes `standardize_pccl.py`, `analyze_principal_diagnosis_sensitivity.py`, and `analyze_functional_sensitivity.py` with `--cohort acute`. Each accepts optional `--data-root` and `--out-dir` arguments and requires only this repository's original cohort exports. `export_severity_tables.py` then writes:

- `results/severity_summary.csv`: crude and PCCL-standardized outcome risks and contrasts.
- `results/pccl_strata.csv`: all seven PCCL strata, with small cells flagged.
- `results/diagnosis_sensitivity.csv`: explicitly defined principal-diagnosis mortality groups.
- `results/functional_sensitivity.csv`: every planned code/outcome, both code-present and code-absent comparisons, including unknown/sparse status rows.
- `results/functional_coverage_bounds.csv`: set-theoretic coverage bounds, not observed unique assessment rates.

Reviewed copies are stored at the repository root. Curated severity rows with fewer than five events or non-events in either arm retain their labels and status but omit numerical count/effect cells. Full flagged audit JSON/CSV stays in Git-ignored `results/`. Rates are proportions and risk differences are on the probability scale.

The revised Word version requires native pagination review; the separately typeset PDF is an independent reading layout and cannot validate Word pagination. Text, references, and editable table contents are checked against the Markdown source.

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
