# Additional acute diagnosis outcomes

These uniquely named files are an addition to the acute manuscript repository. They contain portable local-analysis code, exact query definitions, four model-level E43 results and a field schema. Additional files reproduce the age/principal-diagnosis length-of-stay and existing binary-endpoint analyses, with their aggregate summaries and separate methods documents. No raw workbook, reconstructed stratum table, local source path or source-workbook hash mapping is included. Source workbooks were exported through the official InEK data-browser interface. The analysis scripts operate locally and do not acquire data.

E43 denotes coded unspecified severe protein-energy malnutrition. It is not the broader E40–E44/E46 malnutrition union, whose joint analysis remains pending. The delivery is DRG202601, displayed as “Unterjährige Datenlieferung DRG Januar bis Dezember 2025”. The acute OPS and R13 definitions are in `outcomes_query_plan.json`.

Three models use age/sex/principal diagnosis, age/principal diagnosis/native PCCL, and age/principal diagnosis. A fourth sensitivity coarsens PCCL to 0, 1–2 and 3–6. This fourth model was selected after inspecting sparse native PCCL cells, is explicitly post hoc and does not replace the original models. Sparse and boundary-probability strata remain; coarsening does not establish confidence-interval calibration.

Sex and PCCL are not simultaneously adjusted, NIHSS is unavailable, and PCCL may include outcome-related or downstream diagnoses. These coded associations do not establish a causal dysphagia effect or incident complications. Fixed-weight independent-binomial delta intervals omit hospital clustering, repeated admissions, coding uncertainty and multiplicity adjustment. Model-level interval qualifications are retained in the CSV; detailed cells are withheld.

## Run from the repository root

Python 3.10+ and openpyxl are required. Keep these files together. Obtain workbooks separately in accordance with the provider's conditions. Use an explicit data directory and a private output directory; no machine-specific path is assumed.

```text
python outcomes_analyze_joint.py --data-root ../private_raw --endpoint severe_malnutrition --out-dir ../private_results
python outcomes_verify_joint_e43_independent.py --data-root ../private_raw --aggregate-csv outcomes_severe_malnutrition_joint_aggregate.csv --summary-output ../private_results/e43_independent_summary.json
```

The first command reproduces the three originally specified models and writes detailed audits to the chosen private output directory. The second independently reads the 24 joint denominator/event workbooks and recalculates and checks all four published rows, including the post hoc coarsened-PCCL sensitivity. It does not import the production analysis code. Its default output is a model-level summary only. `--private-audit <path>` explicitly enables detailed local audit output, which must remain private. `--previous-binary-audit <path>` optionally adds comparison with the earlier private single-code calculation.

The additional `outcomes_analyze_los_age_diagnosis.py` and `outcomes_analyze_existing_binary.py` scripts likewise require explicit local data/output directories. See `OUTCOMES_LOS_METHODS.md` and `OUTCOMES_BINARY_METHODS.md` for their exact commands, outcome definitions and limitations. These two analyses adjust age band and principal diagnosis; they must not be described as additionally adjusting sex or PCCL.

The original development QA passed 2,902 checks. The portable validator has a different check count because it compares the sanitized aggregate columns, adds the fourth-row comparison and optionally omits the earlier private audit comparison. These changes do not change the statistical formulas or source-count checks.

For pneumonia only, `--allow-exact-pneumonia-complement` permits the proven full-age-minus-age set difference documented in the plan, saving two native downloads without creating synthetic workbooks or assuming independent margins. All five unfinished clinical endpoints remain explicitly pending in `outcomes_analysis_status.csv`; no unobserved results are reported.

Raw files, source hash mappings, ingestion/runner logs and private audit outputs are excluded from this addition. The statistical extension is post hoc.

## Independent audit of further complete diagnosis endpoints

The additional portable validator `outcomes_verify_joint_independent.py` independently parses the original workbooks and compares all three planned models with the production model-level JSON. It uses 60-digit Decimal arithmetic and does not import production analysis functions. It checks exact cohort, delivery, outcome, age, diagnosis and dysphagia filters; observed integer recovery; nested and disjoint counts; identical denominator support; weighted risks, contrasts, intervals and sparse/boundary diagnostics. Sex and PCCL remain separate models. Its E43 validation passed 3,129 checks. The separate E43-specific validator above remains responsible for the fourth, post hoc coarsened-PCCL row.

```text
python outcomes_verify_joint_independent.py --raw ../private_raw --production-dir ../private_results/aggregate --out-dir ../private_results/independent --endpoint severe_malnutrition
```

After the production analysis of another complete endpoint, select that endpoint or omit `--endpoint` to audit all available production results. Add `--allow-exact-pneumonia-complement` only when using the documented exact pneumonia complement. An endpoint without a completed production result is marked pending and is not estimated. The output directory contains detailed private audit counts and source hashes and must not be published automatically. A separate combined CSV contains only model-level results for endpoints actually validated.

As of 17 November 2026, the remaining 58 native exports comprise 10 pneumonia queries and 12 queries for each of aspiration-related pneumonitis, the pulmonary union, the broad malnutrition union and volume depletion. Only E43 has the complete new three-factor analysis. Existing age/principal-diagnosis-only analyses for individual codes are distinct and must not be confused with these pending three-factor analyses.
