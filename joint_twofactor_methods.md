# Simultaneous two-factor mortality standardization

This is a separate extension of the existing single-factor analyses. It uses eight directly filtered all-principal-diagnosis InEK exports per cohort: two adult age groups multiplied by total cases, dysphagia cases, total deaths, and dysphagia deaths. It produces **age plus PCCL** and, separately, **age plus sex** standardization. It does not imply adjustment for age, sex, PCCL and diagnosis together.

## Source and validation

Use the January-December 2025 under-year DRG delivery, aG-DRG 2025, with the existing cohort OPS and secondary R13.0/R13.1/R13.9 union. Age 18-74 includes seven native age classes (18-29, 30-39, 40-49, 50-54, 55-59, 60-64 and 65-74); age 75+ includes 75-79 and 80+. Death is discharge reason 07. No principal-diagnosis restriction is used.

Each workbook must contain the precise query filters and source delivery. Counts recovered from the stored sex and PCCL fractions must be integers, and every distribution must partition its workbook's case total. The eight new exports must reproduce the adult totals and every native age-class count of the four original cohort exports. Original source filters are also validated. Missing workbooks are not zeros and cause an estimation run to stop.

For each age-by-PCCL or age-by-sex cell, reconstruct non-dysphagia cases as total minus dysphagia cases and non-dysphagia deaths as total deaths minus dysphagia deaths. Verify all counts are nonnegative and deaths cannot exceed their denominator. PCCL levels 0-6 and all four recorded sex categories are retained in the source grid.

## Estimation

Include a stratum only if both groups have a positive denominator. This common-support rule uses denominators, not event counts. Retain supported zero-event strata. Report excluded strata, excluded case counts, and coverage in the total, dysphagia and comparator populations. Recalculate the crude comparison on exactly the retained population for each model.

For stratum g, the fixed reference weight is the pooled number of admissions in that stratum divided by the pooled number across retained strata. Standardized risk in each group is the weighted sum of stratum risks. Under independent-binomial sampling, its conditional variance is the sum of squared weights multiplied by p(1-p)/n. The standardized risk ratio divides the two standardized risks. Its 95% confidence interval uses the log-risk-ratio delta variance; the risk difference uses the sum of the two risk variances. The normal multiplier is 1.959963984540054. An undefined risk ratio or log interval stays undefined, with no continuity correction. Sparse-event and boundary-probability strata are flagged.

Cells with fewer than five events or non-events in either comparison group are flagged as sparse. The implementation reuses the reviewed count validation and fixed-weight standardization primitives from `analyze_joint_standardization.py`. `qa_joint_twofactor.py` independently checks estimates using exact rational arithmetic for synthetic cell counts. Actual-data results additionally require separate raw-workbook count reconstruction and verification.

## Principal diagnoses

The new all-diagnosis exports contain principal-diagnosis marginals within each age band. The module audits whether all nine endcodes of I63 and I61 are explicitly listed in every denominator and death workbook. Unlisted rows remain unknown. It does **not** create a principal-diagnosis-adjusted estimate by selecting complete rows, because suppressed death rows could select the analyzed subset based on the outcome. The separate 24-export design directly queries full I63/I61 groups and is required for the planned three-factor diagnosis analyses.

## Interpretation

The PCCL model is a **joint age-and-PCCL descriptive sensitivity analysis**. PCCL is not an admission NIHSS score and can incorporate diagnoses associated with dysphagia or its consequences. It can therefore overadjust or introduce selection bias; it cannot identify an independent causal effect of dysphagia. Age-by-sex addresses recorded demographic case mix but not clinical severity. Neither model controls for principal diagnosis. Two broad age bands leave residual within-band age differences; the previously completed finer age-only analysis remains complementary.

The target population is adult hospital episodes, not individuals. These data do not account for hospital clustering or repeat admissions. Fixed-weight model intervals do not capture coding uncertainty or confounding. Sparse and boundary-event cells can make approximate intervals less reliable. Only mortality is analyzed here; pneumonia and length of stay are not jointly standardized using this export set.

## Reproduction

```sh
python analyze_joint_twofactor.py --cohort rehab --status-only
python analyze_joint_twofactor.py --cohort rehab
python analyze_joint_twofactor.py --cohort acute
python qa_joint_twofactor.py
```

Use `--cohort both` when both eight-export sets are complete. Defaults are project-relative `raw/` and `results/`; `--raw-dir` and `--out-dir` can override them. A pending run exits with code 2 and does not write estimates. Existing results are not refreshed by status-only or pending runs. Status `available` means files exist; `computed` means the validated estimation completed. The JSON audit output includes detailed source-cell counts and is an internal reproducibility artifact; manuscript/repository summary CSVs contain only aggregate estimates and coverage.
