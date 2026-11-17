# Planned joint mortality standardization

**Status: planned; no real joint estimates until the required new exports are available and validated.** Existing single-factor and functional sensitivity results are separate completed analyses.

## Query design

The actual selected InEK delivery has an age selector but no sex selector. Therefore, each cohort needs **24 exports**: two adult age groups (18–74 and 75+), three principal-diagnosis selections (all diagnoses, full I63, full I61), and four combinations (total, R13-secondary-diagnosis union, total deaths, R13-secondary-diagnosis deaths). The matching cohort-specific `joint_query_plan` contains all exact filenames and code selections.

The 18–74 selection includes the seven native categories from 18–29 through 65–74; 75+ includes 75–79 and 80+. All I63/I61 endcodes are explicitly selected. Death is discharge reason 07. OPS and R13 definitions remain unchanged. No pneumonia query is part of this design.

The four existing original exports (T, D, total deaths, and D deaths) are also required as reference inputs. The new all-diagnosis age queries must reproduce their adult totals and each selected native age-category count exactly. These are already available source files, not four additional browser queries.

For every export, `Info` supplies the full sex and PCCL distributions. Counts are recovered from the stored fractions only after integer and partition checks. Queries must use the same delivery and the correct filters. There is no zero substitution for a missing workbook or a suppressed query; explicit zero-query provenance would need a separate protocol extension.

## Complete diagnosis partition

Within each age group and each sex category, reconstruct:

`other principal diagnoses = all principal diagnoses − I63 − I61`.

Perform that subtraction separately for T, D, deaths in T, and deaths in D, and then derive the comparator C=T−D. Principal diagnoses are mutually exclusive, and the directly selected full I63/I61 populations avoid suppression of individual endcodes. Validate every residual, subgroup, and event count as nonnegative, with events no greater than its denominator. The broad residual is explicitly all remaining diagnoses, not a proxy for one particular disease.

The primary strata are **age group × sex × principal diagnosis**. Include all four recorded sex categories (male, female, diverse, unknown). A separate descriptive sensitivity uses **age group × principal diagnosis × PCCL**. These are separate joint analyses; the available marginals do not provide simultaneous sex×PCCL adjustment.

## Estimation and matching the comparison population

Only cells with both N_D>0 and N_C>0 have common support. Exclude unsupported cells using denominator information only, report their identities and counts, and report coverage separately for total, D, and C. Keep supported cells with zero events. Recalculate the crude comparison on exactly the same retained population as each standardized estimate; do not use the original unrestricted-cohort crude RR as if it were its matched comparator.

For retained joint cell g, use fixed pooled weights w_g=N_Tg/ΣN_Tg. For group j, standardized risk P_j=Σw_g p_jg and variance V_j=Σw_g²p_jg(1−p_jg)/N_jg. The standardized RR is P_D/P_C, with log-scale standard error sqrt(V_D/P_D²+V_C/P_C²); the risk difference is P_D−P_C, with standard error sqrt(V_D+V_C). Normal/delta 95% intervals use z=1.959963984540054. Undefined log intervals at a zero standardized event risk stay undefined; no automatic continuity correction is used.

Sparse event cells and boundary event probabilities are flagged. All intervals assume independent episodes and fixed observed reference weights. They do not cover hospital clustering, repeated admissions, missing coding, or selection bias.

## Interpretation and limits

Age/sex/diagnosis adjustment addresses documented demographic and diagnostic case mix. It does not replace NIHSS or another validated neurological baseline-severity measure. Two age groups leave within-band age differences; existing finer age-only standardization remains a complementary sensitivity. PCCL can incorporate exposure- or outcome-related diagnoses and is not a purely pre-existing severity measure; its joint analysis is explicitly descriptive. No causal dysphagia effect is claimed.

The target is adults. Where common support excludes a sex/diagnosis cell, coverage and exclusions must accompany the estimate. These results cannot be presented as an all-age or unqualified whole-original-cohort analysis.

## Commands and pending behavior

```sh
python analyze_joint_standardization.py --cohort acute --status-only
python analyze_joint_standardization.py --cohort acute
python analyze_joint_standardization.py --cohort rehab --status-only
python analyze_joint_standardization.py --cohort rehab
```

Use `--cohort both` only when both sets are available. `--raw-dir` and `--out-dir` override the default project-relative `raw/` and `results/` directories. Status-only writes availability information and never calculates effects. A normal run with missing inputs writes pending status and exits with code 2, leaving existing result files unrefreshed. A complete run validates all requested cohorts before writing their JSON/CSV estimates. Status `available` means files exist; only status `computed` means they also passed the computational checks.
