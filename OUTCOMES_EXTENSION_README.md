# Additional acute diagnosis outcomes

These uniquely named files are an addition to the acute manuscript repository. They contain portable local-analysis code, exact query definitions, four model-level E43 results and three model-level E86 results, each with a field schema. Additional files reproduce the age/principal-diagnosis length-of-stay and existing binary-endpoint analyses, with their aggregate summaries and separate methods documents. No raw workbook, reconstructed stratum table, local source path or source-workbook hash mapping is included. Source workbooks were exported through the official InEK data-browser interface. The analysis scripts operate locally and do not acquire data.

E43 denotes coded unspecified severe protein-energy malnutrition. It is not the broader E40–E44/E46 malnutrition union, whose joint analysis remains pending. The delivery is DRG202601, displayed as “Unterjährige Datenlieferung DRG Januar bis Dezember 2025”. The acute OPS and R13 definitions are in `outcomes_query_plan.json`.

For E43 and E86, three separate models use age/sex/principal diagnosis, age/principal diagnosis/native PCCL, and age/principal diagnosis. Only E43 has a fourth sensitivity that coarsens PCCL to 0, 1-2 and 3-6. This fourth model was selected after inspecting sparse native PCCL cells, is explicitly post hoc and does not replace the original models. Sparse and boundary-probability strata remain; coarsening does not establish confidence-interval calibration.

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

For pneumonia only, `--allow-exact-pneumonia-complement` permits the proven full-age-minus-age set difference documented in the plan, saving two native downloads without creating synthetic workbooks or assuming independent margins. All four unfinished clinical endpoints remain explicitly pending in `outcomes_analysis_status.csv`; no unobserved results are reported.

Raw files, source hash mappings, ingestion/runner logs and private audit outputs are excluded from this addition. The statistical extension is post hoc.

## Independent audit of further complete diagnosis endpoints

The additional portable validator `outcomes_verify_joint_independent.py` independently parses the original workbooks and compares all three planned models with the production model-level JSON. It uses 60-digit Decimal arithmetic and does not import production analysis functions. It checks exact cohort, delivery, outcome, age, diagnosis and dysphagia filters; observed integer recovery; nested and disjoint counts; identical denominator support; weighted risks, contrasts, intervals and sparse/boundary diagnostics. Sex and PCCL remain separate models. Its E43 validation and its separate E86 validation each passed 3,129 checks. The separate E43-specific validator above remains responsible for the fourth, post hoc coarsened-PCCL row.

```text
python outcomes_verify_joint_independent.py --raw ../private_raw --production-dir ../private_results/aggregate --out-dir ../private_results/independent --endpoint severe_malnutrition
```

After the production analysis of another complete endpoint, select that endpoint or omit `--endpoint` to audit all available production results. Add `--allow-exact-pneumonia-complement` only when using the documented exact pneumonia complement. An endpoint without a completed production result is marked pending and is not estimated. The output directory contains detailed private audit counts and source hashes and must not be published automatically. A separate combined CSV contains only model-level results for endpoints actually validated.

As of 17 November 2026, the remaining 46 native exports comprise 10 pneumonia queries and 12 queries for each of aspiration-related pneumonitis, the pulmonary union and the broad malnutrition union. E43 and E86 have complete separate three-factor analyses. Existing age/principal-diagnosis-only analyses for other individual codes are distinct and must not be confused with the pending three-factor analyses. Use `outcomes_manual_exports_46.csv` or `.md`; the 58-query files are historical snapshots from before E86 completion.

## Completed volume-depletion extension (E86)

All twelve E86 event exports passed delivery, exact-filter, integer-count and denominator checks. E86 denotes coded volume depletion and is not specific for low-intake dehydration. The complete E86 analysis reports three models, with no post hoc coarsened-PCCL E86 result. The primary age-sex-diagnosis RR is 2.87 (95% CI 2.75-2.99); the separate age-diagnosis-PCCL sensitivity RR is 2.12 (approximate 95% CI 2.00-2.26). These intervals are nominal and model based; attenuation after PCCL adjustment is not a causal decomposition.

Public E86 outputs are `outcomes_volume_depletion_joint_aggregate.csv`, its `.schema.json`, and `outcomes_volume_depletion_validation_summary.json`. They contain only complete model-level results and a validation summary. Original exports, source mappings and detailed checks remain private. Supplementary Table S10 contains the E86 models; Table S9 remains specific to E43.

```text
python outcomes_analyze_joint.py --data-root ../private_raw --endpoint volume_depletion --out-dir ../private_results
python outcomes_verify_joint_independent.py --raw ../private_raw --production-dir ../private_results/aggregate --out-dir ../private_results/independent --endpoint volume_depletion
```

The independent E86 audit passed 3,129 checks. This confirms the input selections and numerical reconstruction, not elimination of residual confounding, physiological validation of E86, causal effects, or interval calibration. No sex-by-PCCL cross-classification has been inferred.
