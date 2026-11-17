# Acute manuscript: methods and validation

## Data and exposure

The six original workbooks use **Unterjährige Datenlieferung DRG Januar bis Dezember 2025**. The documented snapshot is 16 January 2026; under-year coding may be incomplete. Exact selections, counts, hashes, and diagnostics are retained in `query_manifest.json`.

The cohort is the case union of OPS 8-981.20–8-981.23, 8-981.30–8-981.33, 8-98b.20–8-98b.23, and 8-98b.30–8-98b.33. This selects a care pathway and duration, not a definitive stroke diagnosis. BfArM permits indications including TIA and ophthalmic ischemia. No adult-age filter was applied; the original cohort includes 22 cases under 18.

D is the unique-case union of R13.0, R13.1, and R13.9 **secondary diagnoses**. The comparator C is total T minus D. It is not necessarily free of clinical dysphagia: principal-diagnosis dysphagia and uncoded dysphagia are not excluded. These R13 categories describe clinical/coding circumstances, not a validated ordinal severity scale.

## Case counting, missing cells, and pneumonia sets

Use case counts rather than mentions. Multiple selections within a field are OR; separate fields are AND. Pneumonia queries use `weitere Nebendiagnosen` to intersect the J12–J18 union with the separate R13 selection. Summing diagnosis or procedure rows can double-count cases. Principal diagnoses are mutually exclusive, but omitted subcodes can be suppressed.

Absent rows are not zero. Diagnosis/procedure `Rest` rows aggregate omitted code rows, not unique-case unions. Visible exclusive partitions are checked against N. Fraction×N is converted to a count only when it agrees with an integer within tolerance. Curated summary endpoints exclude event cells below five; local audit JSON can contain flagged small derived cells and is not a publication table.

Let P be the directly queried secondary J12–J18 union, A be J69.0, and P∩A the J69.0 row within the P export. The combined case union is |P|+|A|−|P∩A|. This specified set does not include every pneumonia etiology. U69.01/U69.04 can coexist and must not be summed as disjoint timing categories; their timing is relative to admission, not dysphagia onset. Adult coding instructions do not by themselves verify individual numerator ages.

## Complementary length-of-stay moments

Let S=Nμ and Q be the sum of squared individual lengths of stay. For a subgroup D nested within T:

\[
N_C=N_T-N_D,\qquad S_C=N_T\mu_T-N_D\mu_D,\qquad Q_C=Q_T-Q_D.
\]

The complementary mean is μ_C=S_C/N_C and sample variance is

\[
s_C^2=\frac{Q_C-S_C^2/N_C}{N_C-1}.
\]

The input SD conventions are empirically different:

- `Info`: sample SD s, Q=(N−1)s²+Nμ².
- `DRG-Verteilung`: population SD σ, Q=N(σ²+μ²).

The diagnostic uses full stored precision and integer hospital days. Acute total Info yields Q=44,828,913 under the sample formula versus 44,829,001.71559 under the population formula. All 438 listed acute-total DRGs give integer Q under the population formula within 9.32×10⁻¹⁰. The six-export evidence is regenerated in `sd_convention_audit.csv`.

This is empirical consistency evidence, not a retrieved official definition of the SD denominator. No such definition was found in the public InEK handbook. It assumes means and SDs summarize the same integer-day observations. Repeat the checks for any new worksheet or delivery and seek provider confirmation before final methods sign-off.

For μ_D−μ_C, use normal-approximation SE sqrt(s_D²/N_D+s_C²/N_C). A population SD contributes variance of the mean σ²/(N−1), equivalent to conversion to sample variance followed by division by N. An N=1 group cannot supply an ordinary variance estimate. Survivor moments subtract deaths with the correct input convention before comparison. Conditioning on discharge alive creates selection; it is not a causal correction.

## Risk contrasts and age-standardized mortality

Mortality is directly selected by discharge reason **07 Tod**. For a/N_D versus b/N_C, RR=(a/N_D)/(b/N_C) and SE(log RR)=sqrt(1/a−1/N_D+1/b−1/N_C). Unstandardized event-rate CIs use Wilson intervals; risk-difference CIs use the independent-binomial normal approximation. RR is undefined when a numerator is zero; no automatic continuity correction is applied.

Direct age standardization uses pooled acute-cohort weights for <65, 65–79, and 80+. Treat observed weights as fixed. For group j, P_j=Σw_g p_jg and V_j=Σw_g²p_jg(1−p_jg)/N_jg. The log standardized-RR SE is sqrt(V_D/P_D²+V_C/P_C²). Broad age bands leave within-band confounding, and <65 includes pediatric cases. These exploratory age-only comparisons are not multivariable risk adjustment.

## Within-DRG standardization

For recoverable DRGs, w_g=N_Dg/ΣN_Dg and the standardized difference is Σw_g(μ_Dg−μ_Cg). Its fixed-weight variance is Σw_g²(s_Dg²/N_Dg+s_Cg²/N_Cg). Report DRG count and D-case coverage because restrictions change the target population.

The base all-comparable analysis contains 171 DRGs; the ≥20-per-arm analysis contains 59. Survivor reconstruction requires explicit death rows in both total and D exports. Omitted death rows cannot be treated as zero. The survivor all-comparable analysis has 58 DRGs, while the ≥20-per-arm analysis has 44; these are separate estimates and neither represents every survivor DRG.

DRG is affected by diagnoses, complications, and procedures and may lie downstream of dysphagia coding. Standardization therefore does not identify an independently adjusted causal effect; attenuation is not a causal proportion explained by case mix. Associated bed-days are descriptive, not demonstrated attributable or preventable days.

All confidence intervals assume independent hospital episodes. Repeated admissions, hospital clustering, coding differences, incomplete reporting, and selection are not covered. For a broad administrative population, these are model-based process intervals, not measurements of coding/completeness uncertainty.

## Procedure definitions and restricted diagnoses

The presentation's EVT material set 8-83b.84/.85/.86/.8a/.8b/.8c identifies selected stentretriever counts and omits aspiration and other retrieval devices. The corrected analysis uses **8-836.80**, intracranial thrombectomy. The original and corrected definitions need not be nested.

Literal **5-431.x** is other gastrostomy, not a wildcard. The full 5-431 family is not synonymous with PEG insertion and includes removal of a buried PEG bumper. A PEG analysis needs an explicit union of intended **5-431.2 descendants**, which remains pending.

I63+I61 denotes cerebral infarction plus intracerebral hemorrhage, not all confirmed strokes; I60, I62, and I64 are excluded. Marginal principal-diagnosis rows permit exact restricted analyses only if every required subcode is visible in every input. Otherwise a direct subgroup query is needed. The code flags incomplete diagnosis-specific mortality groups rather than interpreting absent rows as zero.

## Companion-cohort overlap and outstanding queries

The [companion early-rehabilitation cohort](https://github.com/benlabeit/inek-dysphagia-rehabilitation-2025) may share the same hospital episode with this cohort; patients can also recur across different episodes. No zero-overlap assertion is supported. A single multi-select OPS field forms OR, not the required intersection. Exact episode overlap requires an actual intersection query or a same-universe union plus inclusion-exclusion. Person-level overlap cannot be resolved with these aggregate exports. Do not add cohort totals or associated bed-days as independent national burden.

Outstanding queries include exact episode overlap; principal-diagnosis-restricted outcome exports where subcodes are suppressed; PEG and tracheostomy unions; the original EVT material union for exact slide replication; U69 intersections and verified adult numerator/denominator intersections; richer joint severity/diagnosis adjustment; and the later annual 2025 delivery as a separate sensitivity with its 2026 DRG grouping kept distinct.

## Primary sources

- [InEK handbook](https://datenbrowser.inek.org/assets/manual/InekDatenBrowser.pdf), reviewed version 1 September 2026: delivery definitions, selection logic, suppression; no SD denominator definition located.
- [InEK 2025 under-year delivery procedure](https://www.g-drg.de/einspaltig/content/download/16847/file/Verfahrensbeschreibung_Par_21_Absatz_3b_KHEntgG_2025_20250506.pdf).
- [BfArM acute neurological complex-treatment OPS](https://klassifikationen.bfarm.de/ops/kode-suche/htmlops2025/block-8-97...8-98.htm).
- [BfArM ICD-10-GM R13](https://klassifikationen.bfarm.de/icd-10-gm/kode-suche/htmlgm2025/block-r10-r19.htm).
- [BfArM thrombectomy/material OPS](https://klassifikationen.bfarm.de/ops/kode-suche/htmlops2025/block-8-80...8-85.htm).
- [BfArM gastrostomy OPS](https://klassifikationen.bfarm.de/ops/kode-suche/htmlops2025/block-5-42...5-54.htm).
