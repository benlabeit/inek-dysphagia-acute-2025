# Acute length of stay standardized by age and principal diagnosis

This extension uses the already downloaded InEK January–December 2025 provisional delivery. It adds no source queries. The primary target is adult acute-care hospital episodes, with the same two age bands (18–74 and 75+) and three mutually exclusive principal-diagnosis groups (full I63, full I61 and all remaining diagnoses) used in the joint mortality analyses. The I63 group includes I63.6. The OPS and secondary R13 definitions are unchanged.

The primary analysis reads the 12 age × selected principal diagnosis × exposure workbooks. An explicitly separate survivor sensitivity additionally reads the 12 corresponding death workbooks. Four unrestricted original workbooks provide independent age-count reference checks. Source files are read-only; SHA-256 hashes before and after analysis must agree.

## Recovering length-of-stay moments

Each `Info` worksheet supplies N (`B8`), mean length of stay (`E12`) and SD (`E13`). It supplies sex and PCCL frequencies, but no sex-specific or PCCL-specific length-of-stay means. This analysis therefore adjusts jointly for **age and principal diagnosis only**, not for sex or PCCL.

For each source population, reconstruct the first and second raw moments:

\[
S=N\bar{x},\qquad Q=(N-1)s^2+N\bar{x}^2.
\]

The Info SD is treated as a sample SD. This convention is supported empirically by integer hospital-day moment consistency in every new source. It is not an official provider confirmation of the SD denominator. Before any rounding, both S and Q must be within 0.00001 of an integer; the rounding removes only floating-point representation error. Means and sample SDs must back-calculate to the original stored values. The competing population-SD formula is recorded as a diagnostic. The integer first/second moments then permit exact rational arithmetic in all subsequent calculations.

For each age and exposure selection, derive the other-principal-diagnosis group by subtracting I63 and I61 moments from the all-diagnosis moments. Principal diagnoses are disjoint. Within every age × diagnosis stratum, reconstruct the comparator without selected secondary dysphagia codes by subtracting the dysphagia population from the total population:

\[
N_C=N_T-N_D,\quad S_C=S_T-S_D,\quad Q_C=Q_T-Q_D,
\]

\[
\bar{x}_C=S_C/N_C,\qquad
s_C^2=\frac{Q_C-S_C^2/N_C}{N_C-1}.
\]

Every derived count and moment must be nonnegative, and every variance must be nonnegative. Exact algebraic partition checks require that component N, S and Q recover their parent values. All native age-category counts must match the corresponding unrestricted reference export. Missing or suppressed input files are never treated as zero.

## Standardization and uncertainty

Retain only age × principal-diagnosis strata with cases in both exposure groups. Use the same **pooled population reference principle** as in the mortality standardizations:

\[
w_g=\frac{N_{Tg}}{\sum_g N_{Tg}},\qquad
\mu_j^{std}=\sum_g w_g\bar{x}_{jg},\qquad
\Delta^{std}=\mu_D^{std}-\mu_C^{std}.
\]

With fixed observed reference weights and independent hospital episodes:

\[
\operatorname{Var}(\Delta^{std})=
\sum_g w_g^2\left(\frac{s_{Dg}^2}{N_{Dg}}+\frac{s_{Cg}^2}{N_{Cg}}\right).
\]

Report the normal-approximation 95% confidence interval as the standardized difference ±1.959963984540054 standard errors. If any supported stratum has only one case in an arm, the point estimate remains defined but its ordinary sample-variance CI is unavailable; no variance is imputed. The actual data retain all six strata and contain no such singleton problem.

Recalculate the crude comparison on the exact same supported adult population. Report standardized group means, their difference, confidence limits, stratum weights, N in each group and common-support coverage. The older within-DRG analysis uses dysphagia-case reference weights and a different conditioning variable; its result is a different descriptive estimand and cannot be interpreted as the same adjustment sequence.

## Separate survivor sensitivity

Subtract death-population N, S and Q within each age × diagnosis × exposure group. Reconstruct the survivor comparator and verify that the order of subtracting exposure and death gives identical moments. Standardize to the pooled **survivor** distribution, rather than reusing the total-cohort weights. This analysis conditions on survival and can introduce selection bias. It is not a causal correction for death or a competing-risk analysis.

## Validation and interpretation

`outcomes_analyze_los_age_diagnosis.py` checks source selections and delivery, all age/sex/PCCL partitions, exact moment algebra, common-support weights, original adult counts, and raw-file immutability. The optional `--reference-manifest` argument additionally checks all source hashes, N and exact filter strings against a separately retained, previously verified mortality export manifest. That private manifest is not needed for the standalone calculation. During development, an independent calculation using unrounded Decimal moments at 55-digit precision reproduced the cell moments, variances, reference weights, crude and standardized estimates and confidence limits. The packaged script also independently cross-checks its rational-arithmetic standardized estimates against a floating-point implementation.

This remains a descriptive standardized association. Broad age and diagnosis categories do not eliminate neurological severity confounding; there is no NIHSS, sex or PCCL adjustment in this LOS extension. Confidence intervals do not incorporate repeated admissions, hospital clustering, coding uncertainty, delivery incompleteness or uncertainty in estimated reference weights. Excess days are not established to be caused by dysphagia or preventable through treatment.

## Reproducing the aggregate summary

Use Python 3.10 or newer with `openpyxl`. Both paths are explicit: the source directory is read only, and the output directory should be private.

```text
python outcomes_analyze_los_age_diagnosis.py --data-root PATH_TO_RAW --out-dir PRIVATE_OUTPUT_DIRECTORY
```

The command reproduces `los_age_diagnosis_summary.csv` in the specified output directory. Its two model-level rows correspond to the repository file `outcomes_los_age_diagnosis_summary.csv`. The full primary-plus-survivor analysis requires the 24 joint source workbooks and four original references described above. Filename patterns are `acute_joint_<age18_74|age75plus>_<allhd|i63|i61>_<all|dys|all_death|dys_death>_2025.xlsx` and `acute_<all|dys|all_death|dys_death>_2025.xlsx`.

`--primary-only` needs only the 12 total/dysphagia joint exports and their two original references. `--reference-manifest PATH_TO_PRIVATE_MANIFEST` optionally verifies agreement with a previously checked source manifest. `--raw-dir` remains an alias of `--data-root`.

Only the script, this methods document and the model-level summary CSV are included in this package. The generated `los_age_diagnosis_results.json` contains stratum-level moments and counts; `los_source_audit.json` contains detailed source metadata. Keep both private. Native workbooks, private source manifests, detailed audit outputs and small-cell strata are excluded from the upload package. No permissions to redistribute native InEK files are implied.
