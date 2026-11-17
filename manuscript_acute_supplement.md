# Online Resource 1: Supplementary methods and analyses

**Article:** Dysphagia and inpatient burden in German acute stroke care: a nationwide aggregate-data study

**Journal:** Neurological Research and Practice

**Authors:** Bendix Labeit, Darius Günther Nabavi, Götz Thomalla, Martin Köhrmann, Rainer Dziewas

**Proposed corresponding author:** Bendix Labeit, Department of Neurology, Medical Faculty and University Hospital Düsseldorf, Heinrich Heine University Düsseldorf, Düsseldorf, Germany; bendix.labeit@med.uni-duesseldorf.de

Current affiliations and proposed correspondence require author confirmation for this study. This supplement does not imply that all listed authors have approved the manuscript.

This supplement accompanies the main research article. All analyses are exploratory; no patient-level NIHSS adjustment was possible. Complete candidate functional categories, non-estimable results and model limitations are retained.

# Detailed extraction and statistical methods

## Extraction and quality checks

For diagnoses and procedures, we used the export field “Fälle,” representing episodes with a code, rather than “Nennungen,” representing code mentions. Direct union queries were used for multicode pneumonia endpoints because summing individual code counts can count one episode repeatedly. Comparison-group counts were obtained by subtracting the dysphagia subgroup from the identically defined total cohort. Stored full-precision proportions were converted to counts only when they resolved to integers within numerical tolerance. Suppressed or omitted small cells were not assigned zero.

Counts, cohort filters and totals were reconciled across exports. Length-of-stay reconstruction used the means and second moments for the total and dysphagia groups. Internal checks of second moments for integer-valued lengths of stay supported a sample-standard-deviation convention for the overall “Info” exports and a population-standard-deviation convention for DRG rows. This was an empirical finding from the exports, not an assumed official specification; each convention was converted consistently before calculating uncertainty.

## Statistical analysis

We report proportions, unadjusted risk ratios and risk differences. Proportion intervals used the Wilson method; risk-ratio intervals used the log-Wald method. Mean length-of-stay differences used a normal approximation with separate group variances. The comparator mean and variance were recovered by subtracting the dysphagia group's first and second moments from the corresponding total-cohort moments.

For DRGs with estimable values in both groups, we calculated the within-DRG mean difference and weighted it by the number of episodes with dysphagia in that DRG. Thus, the comparison was standardized to the observed DRG distribution of the dysphagia subgroup. A sensitivity analysis required at least 20 episodes in each group per DRG. Associated bed-days were calculated as the sum of each within-DRG difference multiplied by its dysphagia count. This descriptive quantity is not an attributable or preventable burden estimate.

For exploratory age-standardized mortality, we reconstructed deaths and denominators in three bands: under 65, 65-79 and 80 years or older. Group-specific risks were directly standardized to the pooled age distribution of all 279,277 selected episodes, with weights 24.196%, 36.477% and 39.327%, respectively. The under-65 band included the 22 episodes aged under 18. Confidence intervals for the standardized risk difference and log risk ratio used the delta method with fixed observed weights and independent binomial variances. This comparison addresses broad age composition only; residual differences within bands and other confounding remain. Mortality within principal-diagnosis I61 was reconstructed only after confirming that every expected endcode was present in all four relevant exports. Because I63.6 was omitted from the death tables, an exact cerebral-infarction sensitivity cohort was explicitly restricted to the eight endcodes I63.0-I63.5, I63.8 and I63.9. It was not labeled the full I63 group. Main-diagnosis categories are mutually exclusive, permitting sums of complete endcode sets. These restrictions address diagnostic composition, not severity within a diagnosis.

For PCCL-standardized mortality and J12-J18 pneumonia, the seven PCCL categories (0-6) were confirmed to be exhaustive and mutually exclusive in the total, dysphagia and corresponding outcome-filtered exports. Both exposure groups were represented in every stratum. Group-specific risks were directly standardized to the PCCL distribution of the entire care cohort; intervals used the same fixed-weight binomial delta method as the age analysis. Age and PCCL standardizations were separate analyses. PCCL summarizes the resource-related contribution of coded complications and comorbidities and is not an admission neurological score [InEKPCCL2025]. It can include diagnoses on pathways between dysphagia and outcomes. Consequently, this standardization is descriptive rather than an estimate of a baseline-severity-adjusted causal effect.

Two further mortality analyses simultaneously standardized for age and PCCL, or age and sex, using eight additional exports downloaded on November 17, 2026. Total and dysphagia-coded populations and their corresponding death subsets were directly filtered to ages 18-74 and 75 years or older, comprising seven and two native age categories, respectively. Within each age-filtered export, the PCCL and sex distributions supplied observed joint age-by-PCCL and age-by-sex counts; they were not inferred from unrelated marginal tables. Strata required positive denominators in both groups, while supported zero-event strata were retained. Each model used the pooled distribution of its common-support population as fixed reference weights and recalculated the crude contrast on exactly that population. Confidence intervals used independent binomial stratum variances and the delta method for risk differences and log RRs. Filters, integer counts, native-age totals, event limits and weight sums were verified; an independent workbook reconstruction reproduced the estimates. These were separate two-factor mortality models, without simultaneous control for sex, PCCL and principal diagnosis. They did not jointly standardize pneumonia or length of stay.

The age-filtered design was extended to 24 exports by additionally querying the complete I63 and I61 principal-diagnosis groups within each age, exposure and mortality selection. All nine endcodes in each group were selected directly, including I63.6. The residual group of all other principal diagnoses was reconstructed as the all-diagnosis count minus I63 and I61, separately within each age-by-sex or age-by-PCCL cell and each exposure/outcome population. The mutually exclusive partition was checked for nonnegative counts and valid event denominators. This yielded a three-factor age-by-sex-by-principal-diagnosis model and a separate descriptive age-by-principal-diagnosis-by-PCCL model. The same common-support, fixed pooled-weight, matched-crude and interval methods applied. These directly queried adult diagnosis groups differ from the earlier all-age I63 sensitivity restricted to eight explicitly observed endcodes. Sex and PCCL were not simultaneously included in one model. Sparse strata, defined by fewer than five events or non-events in either exposure group, and boundary risks of zero or one were flagged; missing or suppressed source data were never replaced by zero. The plug-in binomial variance is zero at a boundary, so resulting delta-method intervals may be too optimistic. After reviewing these flags, we performed post hoc influence diagnostics excluding boundary strata or all sparse strata, with reference weights renormalized and crude contrasts recalculated for each retained population. These outcome-dependent exclusions change the target population and are not improved adjustment or alternative causal estimates.

Functional sensitivities compared mortality and J12-J18 pneumonia within each of 21 ICD-10-GM categories representing the Barthel Index, motor Functional Independence Measure (FIM), extended Barthel Index, cognitive FIM and Mini-Mental State Examination (MMSE). Instruments were analyzed separately. The 2025 U50/U51 rules specify assessment during the first five hospital days, or at the beginning of geriatric or early-rehabilitation care, and the highest score within that window when values change [BfArMFunction2025]. Thus, these codes are temporally defined proxies rather than proven pre-dysphagia measurements. The Barthel Index includes eating or PEG self-care, preventing its interpretation as entirely independent of swallowing-related care [BfArMBarthel2025]. Each individual-code analysis required explicit denominator and outcome rows in all four relevant exports. Missing rows were retained as non-estimable rather than zero. All candidate categories and their availability are reported in Supplementary Tables S1-S2. We did not add code counts to infer unique test coverage, combine instruments into one scale, or calculate a multi-category functional standardization without verified episode-level exclusivity. A code-absent group does not indicate normal function. These analyses were developed after inspection of the initial results and remain exploratory.

We also subtracted the death cohorts' counts, sums and second moments from their corresponding total cohorts to derive length of stay among episodes ending in discharge alive. Overall reconstruction used the Info sample-SD convention. Survivor DRG reconstruction used population-SD moments and required an explicitly displayed death row in both the total and dysphagia exports; an absent row could contain suppressed cases and was not treated as zero. The resulting restricted within-DRG comparison was weighted to the included dysphagia-survivor distribution, with coverage reported. These analyses condition on survival and are descriptive sensitivity analyses, not estimates free of mortality-related selection.

The nationwide delivery is not a random sample. The intervals are model-based summaries conditional on the observed data and the applicable observed reference weights. They assume independent episodes and do not account for hospital clustering, repeat admissions, coding error or residual confounding. No patient-level records or admission NIHSS measurements were available. Separate standardized RRs must not be combined into simultaneous adjustment for age, sex, principal diagnosis, functional status and PCCL. Multiple comparisons were considered exploratory; interpretation emphasized magnitude, consistency and clinical context rather than significance thresholds.


# Supplementary tables

## Supplementary Table S1 In hospital mortality within documented functional categories

| Instrument score and code | R13 events / episodes | No R13 events / episodes | RR with 95% CI |
| --- | ---: | ---: | ---: |
| Barthel 100 (U50.00) | 25/369 | 38/17,880 | 31.88 (19.45-52.25) |
| Barthel 80-95 (U50.10) | 20/685 | 66/19,056 | 8.43 (5.14-13.82) |
| Barthel 60-75 (U50.20) | 49/1,101 | 106/16,164 | 6.79 (4.86-9.47) |
| Barthel 40-55 (U50.30) | 139/2,493 | 284/17,768 | 3.49 (2.86-4.25) |
| Barthel 20-35 (U50.40) | 362/4,314 | 483/13,926 | 2.42 (2.12-2.76) |
| Barthel 0-15 (U50.50) | 1,894/9,215 | 2,244/11,843 | 1.08 (1.03-1.15) |
| Motor FIM 85-91 (U50.01) | NR/16 | NR/425 | Not estimable |
| Motor FIM 69-84 (U50.11) | NR/9 | NR/184 | Not estimable |
| Motor FIM 59-68 (U50.21) | NR/11 | NR/103 | Not estimable |
| Motor FIM 43-58 (U50.31) | NR/24 | NR/150 | Not estimable |
| Motor FIM 31-42 (U50.41) | NR/33 | NR/81 | Not estimable |
| Motor FIM 13-30 (U50.51) | 26/246 | 15/124 | 0.87 (0.48-1.59) |
| Extended Barthel 70-90 (U51.00) | 72/1,118 | 115/16,189 | 9.07 (6.80-12.09) |
| Extended Barthel 20-65 (U51.10) | 286/2,342 | 378/6,907 | 2.23 (1.93-2.58) |
| Extended Barthel 0-15 (U51.20) | 334/1,093 | 400/1,332 | 1.02 (0.90-1.15) |
| Cognitive FIM 30-35 (U51.01) | NR/51 | NR/744 | Not estimable |
| Cognitive FIM 11-29 (U51.11) | 14/169 | 15/311 | 1.72 (0.85-3.47) |
| Cognitive FIM 5-10 (U51.21) | 17/119 | 16/77 | 0.69 (0.37-1.28) |
| MMSE 24-30 (U51.02) | 21/692 | 32/4,306 | 4.08 (2.37-7.04) |
| MMSE 17-23 (U51.12) | 35/663 | 37/2,453 | 3.50 (2.22-5.51) |
| MMSE 0-16 (U51.22) | 45/536 | 54/1,240 | 1.93 (1.32-2.83) |

NR indicates that a required source row was absent; this may represent zero or suppressed events and is not assigned zero. Denominators are shown when explicitly available. * Sparse comparison with fewer than five events or non-events in a group, or fewer than 20 episodes in a group; intervals are particularly unstable. FIM, Functional Independence Measure; MMSE, Mini-Mental State Examination. Each row compares R13 coding groups within the named assessment category. Instruments and categories are not pooled into a verified exclusive classification, and rows must not be summed as unique episodes. These exploratory contrasts are not adjusted for age, sex, diagnosis or other functional domains.

## Supplementary Table S2 J12 J18 pneumonia within documented functional categories

| Instrument score and code | R13 events / episodes | No R13 events / episodes | RR with 95% CI |
| --- | ---: | ---: | ---: |
| Barthel 100 (U50.00) | 23/369 | 100/17,880 | 11.14 (7.17-17.33) |
| Barthel 80-95 (U50.10) | 28/685 | 191/19,056 | 4.08 (2.76-6.02) |
| Barthel 60-75 (U50.20) | 77/1,101 | 341/16,164 | 3.32 (2.61-4.21) |
| Barthel 40-55 (U50.30) | 191/2,493 | 726/17,768 | 1.88 (1.61-2.19) |
| Barthel 20-35 (U50.40) | 445/4,314 | 888/13,926 | 1.62 (1.45-1.80) |
| Barthel 0-15 (U50.50) | 1,282/9,215 | 1,245/11,843 | 1.32 (1.23-1.42) |
| Motor FIM 85-91 (U50.01) | NR/16 | NR/425 | Not estimable |
| Motor FIM 69-84 (U50.11) | NR/9 | NR/184 | Not estimable |
| Motor FIM 59-68 (U50.21) | NR/11 | NR/103 | Not estimable |
| Motor FIM 43-58 (U50.31) | NR/24 | NR/150 | Not estimable |
| Motor FIM 31-42 (U50.41) | NR/33 | NR/81 | Not estimable |
| Motor FIM 13-30 (U50.51) | 44/246 | 15/124 | 1.48 (0.86-2.55) |
| Extended Barthel 70-90 (U51.00) | 97/1,118 | 314/16,189 | 4.47 (3.59-5.57) |
| Extended Barthel 20-65 (U51.10) | 297/2,342 | 478/6,907 | 1.83 (1.60-2.10) |
| Extended Barthel 0-15 (U51.20) | 182/1,093 | 151/1,332 | 1.47 (1.20-1.79) |
| Cognitive FIM 30-35 (U51.01) | 5/51 | 9/744 | 8.10 (2.82-23.29) |
| Cognitive FIM 11-29 (U51.11) | 25/169 | 20/311 | 2.30 (1.32-4.02) |
| Cognitive FIM 5-10 (U51.21) | 22/119 | 12/77 | 1.19 (0.62-2.25) |
| MMSE 24-30 (U51.02) | 65/692 | 165/4,306 | 2.45 (1.86-3.23) |
| MMSE 17-23 (U51.12) | 87/663 | 150/2,453 | 2.15 (1.67-2.75) |
| MMSE 0-16 (U51.22) | 61/536 | 118/1,240 | 1.20 (0.89-1.60) |

NR indicates that a required source row was absent; this may represent zero or suppressed events and is not assigned zero. Denominators are shown when explicitly available. * Sparse comparison with fewer than five events or non-events in a group, or fewer than 20 episodes in a group; intervals are particularly unstable. FIM, Functional Independence Measure; MMSE, Mini-Mental State Examination. Each row compares R13 coding groups within the named assessment category. Instruments and categories are not pooled into a verified exclusive classification, and rows must not be summed as unique episodes. These exploratory contrasts are not adjusted for age, sex, diagnosis or other functional domains.

## Supplementary Table S3 Post hoc influence diagnostics for age-by-principal-diagnosis-by-PCCL mortality standardization

| Retained strata | Episodes | Coverage of main common-support population | Standardized RR with approximate 95% CI | Crude RR in the same retained population |
| --- | ---: | ---: | ---: | ---: |
| Main analysis, 41 strata | 279,254 | 100% | 2.19 (2.10-2.29) | 4.71 |
| Excluding 3 boundary-risk strata, 38 strata retained | 250,545 | 89.72% | 2.20 (2.10-2.29) | 4.20 |
| Excluding all 8 sparse strata, 33 strata retained | 240,610 | 86.16% | 2.17 (2.08-2.26) | 4.05 |

Sparse strata have fewer than five events or non-events in either group; boundary strata have observed mortality risk zero or one in either group. Their shares of the main reference weight were 13.84% and 10.28%, respectively. The binomial plug-in variance is zero for a group with a boundary risk, potentially making the main delta-method intervals too optimistic. The exclusions were selected post hoc after reviewing precision flags; the weights were renormalized separately in each retained population. These are outcome-dependent influence diagnostics, not preferred adjustment models, tests of interval calibration or a decomposition of confounding. No small source-cell counts are disclosed.



## Supplementary Table S4 Mutually exclusive pulmonary coding categories

| Category | R13 secondary diagnosis | No R13 secondary diagnosis |
| --- | ---: | ---: |
| J12–J18 without J69.0 | 3,374 (10.03%) | 6,785 (2.76%) |
| J69.0 without J12–J18 | 7,300 (21.70%) | 4,203 (1.71%) |
| Both J12–J18 and J69.0 | 501 (1.49%) | 241 (0.10%) |
| Neither code group | 22,468 (66.78%) | 234,405 (95.43%) |

The four categories sum to the corresponding full group denominator. This partition counts each hospital episode once and avoids double counting coexisting codes. It is a coding classification, not a clinical adjudication of mutually exclusive mechanisms.

## Supplementary Table S5 Length of stay contrasts

| Comparison | Dysphagia episodes covered | Mean difference in days with 95% CI | Associated bed-days |
| --- | ---: | ---: | ---: |
| Overall unadjusted | 33,643 (100%) | 8.85 (8.67–9.04) | 297,899 |
| Within DRGs with estimable values in both groups | 33,063 (98.28%), 171 DRGs | 3.61 (3.45–3.78) | 119,423 |
| Within DRGs with at least 20 episodes per group | 32,105 (95.43%), 59 DRGs | 3.60 (3.44–3.76) | 115,553 |

Mean hospital stay was 16.26 days (sample SD 17.14) with an R13 secondary diagnosis and 7.41 days (sample SD 7.15) without one. Within-DRG means are weighted to the observed distribution of episodes with dysphagia. Associated bed-days multiply observed mean differences by exposed-group counts; they are not estimates of preventable bed-days or economic savings. DRG grouping may itself be influenced by dysphagia, complications and treatment.

## Supplementary Table S6 Exploratory age and survivor analyses

| Analysis | R13 secondary diagnosis | No R13 secondary diagnosis | Contrast with 95% CI |
| --- | ---: | ---: | ---: |
| Mortality, age under 65 | 250/4,756 (5.26%) | 683/62,818 (1.09%) | RR 4.83 (4.20-5.57) |
| Mortality, age 65-79 | 1,284/11,240 (11.42%) | 2,150/90,633 (2.37%) | RR 4.82 (4.51-5.15) |
| Mortality, age 80 or older | 3,469/17,647 (19.66%) | 4,913/92,183 (5.33%) | RR 3.69 (3.54-3.84) |
| Mortality, directly age-standardized | 13.1696%; underlying n = 33,643 | 3.22435%; underlying n = 245,634 | RR 4.08 (3.95-4.23) |
| Stay among episodes ending in discharge alive | n = 28,640; 16.72 days (SD 17.63) | n = 237,888; 7.32 days (SD 6.97) | Difference 9.40 days (9.19-9.60) |
| Restricted survivor within-DRG comparison | n = 27,222; 95.05% of dysphagia survivors | n = 228,798; 58 common DRGs | Difference 3.59 days (3.41-3.78) |

The standardized mortality rates are weighted risks, not observed event counts; the reference is the pooled three-band age distribution of the full OPS cohort. Survivor SDs are sample SDs reconstructed from moments. The restricted survivor DRG comparison uses only exactly reconstructable strata and is weighted to the included dysphagia-survivor distribution. Its comparator count describes available episodes rather than the analysis weights. Confidence intervals are model-based and do not account for clustering or residual confounding. The restricted I63 sensitivity in Supplementary Table S7 excludes I63.6 explicitly; no result is inferred for the omitted I63.6 death rows. All analyses in this table are exploratory.

## Supplementary Table S7 Administrative complexity, simultaneous standardization and clinical subgroup sensitivities

| Analysis | R13 secondary diagnosis | No R13 secondary diagnosis | RR with 95% CI |
| --- | ---: | ---: | ---: |
| Mortality standardized by PCCL | 11.47% | 3.59% | 3.20 (3.07-3.33) |
| J12-J18 pneumonia standardized by PCCL | 6.99% | 3.39% | 2.07 (1.97-2.16) |
| Adult mortality standardized jointly by age and PCCL | 10.09% | 3.64% | 2.78 (2.67-2.89) |
| Adult mortality standardized jointly by age and sex | 13.50% | 3.21% | 4.21 (4.07-4.36) |
| Adult mortality standardized jointly by age, sex and principal diagnosis | 13.39% | 3.37% | 3.98 (3.82-4.14) |
| Adult mortality standardized jointly by age, principal diagnosis and PCCL | 8.46% | 3.86% | 2.19 (2.10-2.29) |
| Mortality principal I63 excluding I63.6 | 3,871/26,604 (14.55%) | 5,556/149,351 (3.72%) | 3.91 (3.76-4.07) |
| Mortality principal I61 | 611/3,364 (18.16%) | 1,084/8,784 (12.34%) | 1.47 (1.34-1.61) |
| Mortality Barthel Index 0-15 U50.50 | 1,894/9,215 (20.55%) | 2,244/11,843 (18.95%) | 1.08 (1.03-1.15) |
| Mortality extended Barthel Index 0-15 U51.20 | 334/1,093 (30.56%) | 400/1,332 (30.03%) | 1.02 (0.90-1.15) |

Single-factor PCCL rows use the pooled distribution of all 279,277 episodes across seven PCCL categories. Joint models use ages 18-74 and 75+ and fixed pooled common-support weights. Two-factor coverage: age-by-PCCL, 14/14 strata and 279,255 episodes (33,641 dysphagia; 245,614 comparison); age-by-sex, 4/8 strata and 279,248 episodes (33,641 dysphagia; 245,607 comparison). Three-factor coverage: age-by-sex-by-diagnosis, 12/24 strata and 279,248 episodes (33,641 dysphagia; 245,607 comparison); age-by-diagnosis-by-PCCL, 41/42 strata and 279,254 episodes (33,640 dysphagia; 245,614 comparison). Three-factor diagnosis groups are complete directly queried I63 (including I63.6), complete I61 and all remaining principal diagnoses. Sex and PCCL are never jointly included. The approximate age-diagnosis-PCCL interval may be too optimistic because boundary-risk strata have zero plug-in variance; Supplementary Table S3 reports post hoc influence diagnostics. The remaining rows are crude comparisons in all-age clinical subgroups; the earlier I63 row explicitly excludes I63.6. Functional subgroups may overlap and are not a partition of the full cohort. All 21 candidate functional categories, including non-estimable results, appear in Supplementary Tables S1-S2. No model controls all baseline risk factors. All analyses and intervals are exploratory and model-based.


# Supplementary literature search appendix

## Search date and scope

The targeted narrative search was performed on November 16, 2026. Web search was used to locate original PubMed records, publisher-hosted articles and accessible PubMed Central full texts. Primary studies of acute stroke dysphagia, respiratory complications, mortality, hospital stay, resource use, assessment, feeding and rehabilitation interventions were prioritized. German and other nationwide cohorts were particularly relevant. Clinical and reporting guidelines were included for recommendations and methodology, not treated as primary outcome studies.

No lower publication-year limit was imposed, preserving landmark screening and feeding trials. One explicit recent-literature query used a 730-day recency filter; the other queries had no recency restriction. English- and German-language sources were eligible. The search did not include a complete database export, formal duplicate screening, a risk-of-bias instrument or quantitative pooling. It should be described as a targeted narrative search, not a systematic review. Full texts were inspected selectively where accessible; several study summaries rely on their primary abstracts. The bibliography was verified against primary records for title, year, journal, DOI and PMID.

## Executed query strings

1. post stroke dysphagia nationwide administrative database mortality length of stay aspiration pneumonia study Germany InEK Ungerer 2026
2. post stroke dysphagia hospital outcomes national inpatient sample Patel 2018 dysphagia
3. European Stroke Organisation European Society Swallowing Disorders guideline diagnosis treatment post stroke dysphagia 2021 Dziewas
4. German FEES registry 2019 safety clinical impact neurological patients Dziewas prospective multicenter
5. dysphagia acute stroke registry screening pneumonia mortality Al-Khaled 2016 12000
6. Bray dysphagia screening stroke associated pneumonia delay 2017 stroke national audit
7. Arnold Liesirova Broeg-Morvay Meisterander Schlager dysphagia acute stroke incidence burden outcome 2016
8. stroke dysphagia screening Hinchey 2005 Titsworth 2013 pneumonia prospective quality improvement
9. dysphagia acute stroke Al-Khaled 2016 screening 12000 pneumonia mortality
10. Bray dysphagia screening stroke associated pneumonia delay 2017 national audit
11. Arnold Liesirova Broeg-Morvay dysphagia acute stroke incidence burden outcome 2016
12. stroke dysphagia screening Hinchey 2005 Titsworth 2013 pneumonia
13. Labeit FEES acute stroke hospital implementation pneumonia flexible endoscopic swallowing study 2020 2021 2022 PubMed
14. Suntrup Krueger 2018 dysphagia 674423 157 hospitals 10.1159
15. stroke dysphagia Bonilha 2014 economic burden hospital costs 12 month PubMed
16. Galovic 2019 development validation prognostic model swallowing recovery oral intake ischemic stroke PubMed FOOD trial Dennis 2005
17. "Costs of post-stroke dysphagia during acute hospitalization" PubMed
18. "Development and implementation of a swallowing screen" "Lancet" stroke Middleton fever sugar swallowing 2011
19. "Effect of timing and method of enteral tube feeding" PubMed
20. "Dysphagia in Patients with Acute Ischemic Stroke" "doi" Al-Khaled
21. "The association between delays in screening" "doi" "Bray"
22. "Formal dysphagia screening protocols prevent pneumonia" doi
23. "Prospective quality initiative to maximize dysphagia screening" doi
24. "Implementation of evidence-based treatment protocols" "QASC" PubMed
25. site:pubmed.ncbi.nlm.nih.gov "RECORD" "Benchimol" 2015
26. site:pubmed.ncbi.nlm.nih.gov "Diagnosis of Stroke-Associated Pneumonia" "2015"
27. "Early flexible endoscopic evaluation of swallowing after mechanical thrombectomy" DOI
28. post stroke dysphagia administrative nationwide inpatient 2025 2026 study — recency filter: 730 days.
29. "One-Year Risk of Pneumonia and Mortality" "doi"
30. "Healthcare costs of post-stroke oropharyngeal dysphagia" "doi"
31. "Adjustment of oral diet based on flexible" "authors"
32. "An Exploratory Classification Framework" PubMed
33. site:pubmed.ncbi.nlm.nih.gov PHAST-TRAC 2018 pharyngeal electrical stimulation tracheotomised stroke
34. site:pubmed.ncbi.nlm.nih.gov STROBE 2007 von Elm PLoS medicine e296
35. "The Effect of Improved Dysphagia Care" "45" "101"
36. "European Stroke Organisation" "34746431" "2021"
37. "40489041"
38. "Dysphagia Management is Associated with Reduced Mortality"

The 2026 DESIRE cohort and 2025 Austrian registry were additionally identified through a parallel relevance/freshness search and independently checked via [PubMed 42964110](https://pubmed.ncbi.nlm.nih.gov/42964110/) and [PubMed 40489041](https://pubmed.ncbi.nlm.nih.gov/40489041/). Publisher and PubMed pages were also opened directly for DOI/PMID verification. Queries 5–8 had truncated combined output and were followed by the more targeted queries 9–12; no retrieval totals were inferred from this sequence.

## Evidence interpretation

The combined bibliography contains 39 journal publications plus eight official data or coding sources. It includes clinical cohorts, nationwide registries, administrative analyses, randomized trials, a consensus definition and reporting/clinical guidelines. Effect measures retain their original meaning: published adjusted odds ratios and hazard ratios are not directly equated to the current unadjusted risk ratios.

Ungerer 2026 is a direct predecessor using German national DRG data, so the current manuscript makes no first-national-FEES-analysis claim. The main incremental contribution is the 2025 inpatient burden analysis, exact handling of overlapping pulmonary diagnoses, descriptive DRG-stratified hospital-stay comparison, and transparently bounded diagnosis, PCCL and functional sensitivities. Ho 2018 defines dysphagia through nasogastric-tube use and therefore represents a different phenotype. Vasan 2023 supplies a counterexample to uniformly increased inpatient mortality in coding-based studies. Horn 2026 is exploratory and does not validate a severity score for German R13 codes. QASC evaluates a multicomponent bundle; PHAST-TRAC evaluates a selected tracheotomized population. Their results cannot be generalized into an efficacy claim for procedures recorded in these exports.

The narrative search was updated on November 17, 2026 with author-specific PubMed screening documented below. Final author review should check the wording against complete texts of retained references. Reference selection supports contextual interpretation rather than a systematic evidence synthesis.

## Author-specific PubMed update on November 17, 2026

The update screened all PubMed records returned for Bendix Labeit, including coauthored papers, reviews, letters and corrections. The query “Labeit B” in the Author field returned 66 records; “Labeit Bendix” in the Full Author Name field returned 65; “Labeit BR” in the Author field and “Labeit Bendix Ruven” in the Full Author Name field returned none. Pagination with 20 results per page at offsets 0, 20, 40 and 60 reproduced the same 66 unique identifiers. Searches using the verified author identifier and the author surname combined with dysphagia/swallowing terms found no additional records. The record indexed with initials only (PMID 41860704) was matched using the Düsseldorf affiliation and email. No record published after the search date was included.

All 66 records were individually assessed using primary PubMed metadata and available abstracts; selected full texts were examined for claims requiring clarification. Twenty records were identified as potentially relevant to the acute manuscript and 21 to the companion rehabilitation manuscript, with 28 in their union. These are candidate counts, not independent-study counts or a requirement to cite every paper. Fourteen acute candidates informed the final article. Six additional candidates concerned overlapping narrative reviews, sensory mechanisms, extubation-prediction scores or a nonrandomized pre-extubation intervention and were not needed for the specific claims retained. Review articles provide clinical context rather than trial-effect estimates. The original PES pilot and its recovery and economic follow-up represent one 60-patient trial, not three independent studies.

The scope is complete for these PubMed queries as retrieved on the search date, not for publications absent from PubMed. This author-specific update supplements the broader narrative search; it is neither a systematic review of all dysphagia literature nor a comprehensive full-text risk-of-bias appraisal. The 66-record search and per-record relevance decisions are retained in research/labeit_pubmed_screening_20261117.json and .csv. Bibliographic metadata and screening decisions accompany the reproducibility materials; full source XML records and abstracts are retained only in local verification files and are not redistributed. The final bibliography contains 39 journal publications and eight official data/classification sources; inclusion reflects support for particular claims rather than author identity alone.

## Reproducibility files for simultaneous analyses

The simultaneous two-factor mortality analyses are implemented in analyze_joint_twofactor.py, with methods in joint_twofactor_methods.md and aggregate estimates and coverage in acute_joint_twofactor.csv. The implementation passed 22 checks recorded in joint_twofactor_validation.json, and the acute-cohort estimates were independently verified against the original Excel workbooks using exact-rational risk and variance calculations (acute_joint_twofactor_independent_qa.json: passed). The detailed acute_joint_twofactor.json contains internal source-cell audit data and is not a public-data supplement.

The three-factor analyses use analyze_joint_standardization.py, joint_standardization_methods.md and the 24-export acute joint query plan. Aggregate estimates and coverage are provided in acute_joint_standardization.csv. Independent workbook reconstruction reproduced the risks, weights and intervals (acute_joint_standardization_independent_qa.json: passed). Detailed cell counts in acute_joint_standardization.json are internal audit data, not a public-data supplement.

Post hoc influence diagnostics are implemented in analyze_joint_influence.py using the command `python analyze_joint_influence.py --cohort acute`; aggregate outputs are acute_joint_influence.csv and acute_joint_influence.json. These reproducibility outputs do not disclose small source-cell counts.


# References

1. **[AlKhaled2016]** Al-Khaled M, Matthis C, Binder A, et al. Dysphagia in Patients with Acute Ischemic Stroke: Early Dysphagia Screening May Reduce Stroke-Related Pneumonia and Improve Stroke Outcomes. Cerebrovasc Dis. 42(1-2):81-89. 2016. [DOI 10.1159/000445299](https://doi.org/10.1159/000445299); [PMID 27074007](https://pubmed.ncbi.nlm.nih.gov/27074007/).

2. **[Arnold2016]** Arnold M, Liesirova K, Broeg-Morvay A, et al. Dysphagia in Acute Stroke: Incidence, Burden and Impact on Clinical Outcome. PLoS One. 11(2):e0148424. 2016. [DOI 10.1371/journal.pone.0148424](https://doi.org/10.1371/journal.pone.0148424); [PMID 26863627](https://pubmed.ncbi.nlm.nih.gov/26863627/).

3. **[Bray2017]** Bray BD, Smith CJ, Cloud GC, et al. The association between delays in screening for and assessing dysphagia after acute stroke, and the risk of stroke-associated pneumonia. J Neurol Neurosurg Psychiatry. 88(1):25-30. 2017. [DOI 10.1136/jnnp-2016-313356](https://doi.org/10.1136/jnnp-2016-313356); [PMID 27298147](https://pubmed.ncbi.nlm.nih.gov/27298147/).

4. **[Hinchey2005]** Hinchey JA, Shephard T, Furie K, et al. Formal dysphagia screening protocols prevent pneumonia. Stroke. 36(9):1972-1976. 2005. [DOI 10.1161/01.STR.0000177529.86868.8d](https://doi.org/10.1161/01.STR.0000177529.86868.8d); [PMID 16109909](https://pubmed.ncbi.nlm.nih.gov/16109909/).

5. **[Titsworth2013]** Titsworth WL, Abram J, Fullerton A, et al. Prospective quality initiative to maximize dysphagia screening reduces hospital-acquired pneumonia prevalence in patients with stroke. Stroke. 44(11):3154-3160. 2013. [DOI 10.1161/STROKEAHA.111.000204](https://doi.org/10.1161/STROKEAHA.111.000204); [PMID 23963330](https://pubmed.ncbi.nlm.nih.gov/23963330/).

6. **[SuntrupKrueger2018]** Suntrup-Krueger S, Minnerup J, Muhle P, et al. The Effect of Improved Dysphagia Care on Outcome in Patients with Acute Stroke: Trends from 8-Year Data of a Large Stroke Register. Cerebrovasc Dis. 45(3-4):101-108. 2018. [DOI 10.1159/000487811](https://doi.org/10.1159/000487811); [PMID 29533960](https://pubmed.ncbi.nlm.nih.gov/29533960/).

7. **[Dziewas2021Guideline]** Dziewas R, Michou E, Trapl-Grundschober M, et al. European Stroke Organisation and European Society for Swallowing Disorders guideline for the diagnosis and treatment of post-stroke dysphagia. Eur Stroke J. 6(3):LXXXIX-CXV. 2021. [DOI 10.1177/23969873211039721](https://doi.org/10.1177/23969873211039721); [PMID 34746431](https://pubmed.ncbi.nlm.nih.gov/34746431/).

8. **[Dziewas2019Registry]** Dziewas R, Auf dem Brinke M, Birkmann U, et al. Safety and clinical impact of FEES - results of the FEES-registry. Neurol Res Pract. 1:16. 2019. [DOI 10.1186/s42466-019-0021-5](https://doi.org/10.1186/s42466-019-0021-5); [PMID 33324882](https://pubmed.ncbi.nlm.nih.gov/33324882/).

9. **[Ungerer2026]** Ungerer MN, Bartig D, Moreno Agredo A, Braun T, Gumbinger C Fiberoptic endoscopic evaluation of swallowing in German stroke units: a retrospective diagnosis-related group analysis (2019-2024). Neurol Res Pract. 8:46. 2026. [DOI 10.1186/s42466-026-00506-3](https://doi.org/10.1186/s42466-026-00506-3); [PMID 42277987](https://pubmed.ncbi.nlm.nih.gov/42277987/).

10. **[Vasan2023]** Vasan V, Hardigan TA, Ali M, et al. Dysphagia after ischemic and hemorrhagic stroke: A propensity-matched 20-year analysis of the national inpatient sample. J Stroke Cerebrovasc Dis. 32(9):107295. 2023. [DOI 10.1016/j.jstrokecerebrovasdis.2023.107295](https://doi.org/10.1016/j.jstrokecerebrovasdis.2023.107295); [PMID 37544059](https://pubmed.ncbi.nlm.nih.gov/37544059/).

11. **[Ho2018]** Ho CH, Lin WC, Hsu YF, Lee IH, Hung YC One-Year Risk of Pneumonia and Mortality in Patients with Poststroke Dysphagia: A Nationwide Population-Based Study. J Stroke Cerebrovasc Dis. 27(5):1311-1317. 2018. [DOI 10.1016/j.jstrokecerebrovasdis.2017.12.017](https://doi.org/10.1016/j.jstrokecerebrovasdis.2017.12.017); [PMID 29395642](https://pubmed.ncbi.nlm.nih.gov/29395642/).

12. **[Labeit2023Costs]** Labeit B, Kremer A, Muhle P, Claus I, Warnecke T, Dziewas R, Suntrup-Krueger S Costs of post-stroke dysphagia during acute hospitalization from a health-insurance perspective. Eur Stroke J. 8(1):361-369. 2023. [DOI 10.1177/23969873221147740](https://doi.org/10.1177/23969873221147740); [PMID 37021194](https://pubmed.ncbi.nlm.nih.gov/37021194/).

13. **[Bonilha2014]** Bonilha HS, Simpson AN, Ellis C, Mauldin P, Martin-Harris B, Simpson K The one-year attributable cost of post-stroke dysphagia. Dysphagia. 29(5):545-552. 2014. [DOI 10.1007/s00455-014-9543-8](https://doi.org/10.1007/s00455-014-9543-8); [PMID 24948438](https://pubmed.ncbi.nlm.nih.gov/24948438/).

14. **[Marin2021]** Marin S, Serra-Prat M, Ortega O, et al. Healthcare costs of post-stroke oropharyngeal dysphagia and its complications: malnutrition and respiratory infections. Eur J Neurol. 28(11):3670-3681. 2021. [DOI 10.1111/ene.14998](https://doi.org/10.1111/ene.14998); [PMID 34176195](https://pubmed.ncbi.nlm.nih.gov/34176195/).

15. **[Braun2019]** Braun T, Juenemann M, Viard M, et al. Adjustment of oral diet based on flexible endoscopic evaluation of swallowing (FEES) in acute stroke patients: a cross-sectional hospital-based registry study. BMC Neurol. 19(1):282. 2019. [DOI 10.1186/s12883-019-1499-8](https://doi.org/10.1186/s12883-019-1499-8); [PMID 31718562](https://pubmed.ncbi.nlm.nih.gov/31718562/).

16. **[Pinho2024]** Pinho J, Meyer T, Mall B, et al. Early flexible endoscopic evaluation of swallowing after mechanical thrombectomy in stroke patients. Ann Clin Transl Neurol. 11(3):757-767. 2024. [DOI 10.1002/acn3.51998](https://doi.org/10.1002/acn3.51998); [PMID 38217067](https://pubmed.ncbi.nlm.nih.gov/38217067/).

17. **[Galovic2019]** Galovic M, Stauber AJ, Leisi N, et al. Development and Validation of a Prognostic Model of Swallowing Recovery and Enteral Tube Feeding After Ischemic Stroke. JAMA Neurol. 76(5):561-570. 2019. [DOI 10.1001/jamaneurol.2018.4858](https://doi.org/10.1001/jamaneurol.2018.4858); [PMID 30742198](https://pubmed.ncbi.nlm.nih.gov/30742198/).

18. **[Dennis2005FOOD]** Dennis MS, Lewis SC, Warlow C; FOOD Trial Collaboration Effect of timing and method of enteral tube feeding for dysphagic stroke patients (FOOD): a multicentre randomised controlled trial. Lancet. 365(9461):764-772. 2005. [DOI 10.1016/S0140-6736(05)17983-5](https://doi.org/10.1016/S0140-6736(05)17983-5); [PMID 15733717](https://pubmed.ncbi.nlm.nih.gov/15733717/).

19. **[Middleton2011QASC]** Middleton S, McElduff P, Ward J, et al.; QASC Trialists Group Implementation of evidence-based treatment protocols to manage fever, hyperglycaemia, and swallowing dysfunction in acute stroke (QASC): a cluster randomised controlled trial. Lancet. 378(9804):1699-1706. 2011. [DOI 10.1016/S0140-6736(11)61485-2](https://doi.org/10.1016/S0140-6736(11)61485-2); [PMID 21996470](https://pubmed.ncbi.nlm.nih.gov/21996470/).

20. **[Dziewas2018PHAST]** Dziewas R, Stellato R, van der Tweel I, et al.; PHAST-TRAC investigators Pharyngeal electrical stimulation for early decannulation in tracheotomised patients with neurogenic dysphagia after stroke (PHAST-TRAC): a prospective, single-blinded, randomised trial. Lancet Neurol. 17(10):849-859. 2018. [DOI 10.1016/S1474-4422(18)30255-2](https://doi.org/10.1016/S1474-4422(18)30255-2); [PMID 30170898](https://pubmed.ncbi.nlm.nih.gov/30170898/).

21. **[Horn2026]** Horn J, Simpson KN, Simpson AN, Bonilha LF, Bonilha HS An Exploratory Classification Framework for Poststroke Dysphagia Severity Using Administrative Data: Administrative Data Dysphagia Severity Scale. Am J Speech Lang Pathol. 35(1):98-108. 2026. [DOI 10.1044/2025_AJSLP-24-00313](https://doi.org/10.1044/2025_AJSLP-24-00313); [PMID 41124314](https://pubmed.ncbi.nlm.nih.gov/41124314/).

22. **[Smith2015PISCES]** Smith CJ, Kishore AK, Vail A, et al. Diagnosis of Stroke-Associated Pneumonia: Recommendations From the Pneumonia in Stroke Consensus Group. Stroke. 46(8):2335-2340. 2015. [DOI 10.1161/STROKEAHA.115.009617](https://doi.org/10.1161/STROKEAHA.115.009617); [PMID 26111886](https://pubmed.ncbi.nlm.nih.gov/26111886/).

23. **[Benchimol2015RECORD]** Benchimol EI, Smeeth L, Guttmann A, et al.; RECORD Working Committee The REporting of studies Conducted using Observational Routinely-collected health Data (RECORD) statement. PLoS Med. 12(10):e1001885. 2015. [DOI 10.1371/journal.pmed.1001885](https://doi.org/10.1371/journal.pmed.1001885); [PMID 26440803](https://pubmed.ncbi.nlm.nih.gov/26440803/).

24. **[vonElm2007STROBE]** von Elm E, Altman DG, Egger M, Pocock SJ, Gotzsche PC, Vandenbroucke JP; STROBE Initiative The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) statement: guidelines for reporting observational studies. PLoS Med. 4(10):e296. 2007. [DOI 10.1371/journal.pmed.0040296](https://doi.org/10.1371/journal.pmed.0040296); [PMID 17941714](https://pubmed.ncbi.nlm.nih.gov/17941714/).

25. **[Selg2026]** Selg J, Mirkoska V, Holmlund T, et al. Incidence of dysphagia in acute stroke patients—a prospective multicentre cohort study. Front Neurol. 17:1886254. 2026. [DOI 10.3389/fneur.2026.1886254](https://doi.org/10.3389/fneur.2026.1886254); [PMID 42964110](https://pubmed.ncbi.nlm.nih.gov/42964110/).

26. **[Hotz2025]** Hotz JF, Kaindl L, Schneider L, et al.; Austria Stroke Unit Registry Collaborators Dysphagia Management is Associated with Reduced Mortality in Patients with Moderate to Severe Acute Ischemic Stroke. Neurol Ther. 14(4):1539-1552. 2025. [DOI 10.1007/s40120-025-00783-1](https://doi.org/10.1007/s40120-025-00783-1); [PMID 40489041](https://pubmed.ncbi.nlm.nih.gov/40489041/).

27. **[Labeit2023Assessment]** Labeit B, Michou E, Hamdy S, et al. (2023) The assessment of dysphagia after stroke: state of the art and future directions. Lancet Neurol 22:858–870. https://doi.org/10.1016/S1474-4422(23)00153-9. [PMID 37596008](https://pubmed.ncbi.nlm.nih.gov/37596008/).

28. **[Labeit2024Treatment]** Labeit B, Michou E, Trapl-Grundschober M, et al. (2024) Dysphagia after stroke: research advances in treatment interventions. Lancet Neurol 23:418–428. https://doi.org/10.1016/S1474-4422(24)00053-X. [PMID 38508837](https://pubmed.ncbi.nlm.nih.gov/38508837/).

29. **[Lueg2026GEMIDAS]** Lueg G, Willschrei P, Pourhassan M, et al. (2026) Dysphagia as a geriatric syndrome: nationwide outcomes from the GEMIDAS registry. Arch Gerontol Geriatr 150:106341. https://doi.org/10.1016/j.archger.2026.106341. [PMID 42361766](https://pubmed.ncbi.nlm.nih.gov/42361766/).

30. **[Lueg2026Dehydration]** Lueg G, Funk L, Labeit B, et al. (2026) In-hospital mortality in co-occurring dehydration and dysphagia: results from the nationwide GEMIDAS Pro registry. Eur Geriatr Med. https://doi.org/10.1007/s41999-026-01627-3. [PMID 42862540](https://pubmed.ncbi.nlm.nih.gov/42862540/).

31. **[Marae2026FEESAccess]** Marae JG, Masanneck L, Pawlitzki M, et al. (2026) Mapping neurogenic dysphagia diagnostics in Germany: accessibility, implementation practices, and barriers to swallowing endoscopy. Neurol Res Pract 8:17. https://doi.org/10.1186/s42466-026-00473-9. [PMID 41851886](https://pubmed.ncbi.nlm.nih.gov/41851886/).

32. **[Suntrup2023PES]** Suntrup-Krueger S, Labeit B, Marian T, et al. (2023) Pharyngeal electrical stimulation for postextubation dysphagia in acute stroke: a randomized controlled pilot trial. Crit Care 27:383. https://doi.org/10.1186/s13054-023-04665-6. [PMID 37789340](https://pubmed.ncbi.nlm.nih.gov/37789340/).

33. **[Suntrup2025PES]** Suntrup-Krueger S, Labeit B, von Itter J, et al. (2025) Treating postextubation dysphagia after stroke with pharyngeal electrical stimulation -insights from a randomized controlled pilot trial. Neurotherapeutics 22:e00613. https://doi.org/10.1016/j.neurot.2025.e00613. [PMID 40383663](https://pubmed.ncbi.nlm.nih.gov/40383663/).

34. **[Labeit2026PESCosts]** Labeit B, Jung A, von Itter J, et al. (2026) Pharyngeal electrical stimulation for postextubation dysphagia after stroke: a randomized trial on hospitalization costs from a health insurance perspective. Sci Rep 16:8556. https://doi.org/10.1038/s41598-026-43591-9. [PMID 41803360](https://pubmed.ncbi.nlm.nih.gov/41803360/).

35. **[Labeit2018NIHSS]** Labeit B, Mueller H, Muhle P, et al. (2018) Predicting Dysphagia with National Institute of Health Stroke Scale: Distinction between Infra- and Supratentorial Region is Essential. Cerebrovasc Dis 46:152–160. https://doi.org/10.1159/000493371. [PMID 30253410](https://pubmed.ncbi.nlm.nih.gov/30253410/).

36. **[Labeit2022FEESVFSS]** Labeit B, Ahring S, Boehmer M, et al. (2022) Comparison of Simultaneous Swallowing Endoscopy and Videofluoroscopy in Neurogenic Dysphagia. J Am Med Dir Assoc 23:1360–1366. https://doi.org/10.1016/j.jamda.2021.09.026. [PMID 34678269](https://pubmed.ncbi.nlm.nih.gov/34678269/).

37. **[Dziewas2024IntegratedFEES]** Dziewas R, Warnecke T, Labeit B, et al. (2024) Systematic approach to contextualize findings of flexible endoscopic evaluation of swallowing in neurogenic dysphagia- towards an integrated FEES report. Neurol Res Pract 6:26. https://doi.org/10.1186/s42466-024-00321-8. [PMID 38720388](https://pubmed.ncbi.nlm.nih.gov/38720388/).

38. **[Warnecke2021Classification]** Warnecke T, Labeit B, Schroeder J, et al. (2021) Neurogenic Dysphagia: Systematic Review and Proposal of a Classification System. Neurology 96:e876–e889. https://doi.org/10.1212/WNL.0000000000011350. [PMID 33318164](https://pubmed.ncbi.nlm.nih.gov/33318164/).

39. **[Jung2026CoughStroke]** Jung A, Labeit B, Oelenberg S, et al. (2026) Cough reflex testing for dysphagia severity and pneumonia risk after acute stroke: a prospective observational study. Stroke Vasc Neurol. https://doi.org/10.1136/svn-2026-005197. [PMID 42276582](https://pubmed.ncbi.nlm.nih.gov/42276582/).

## Data and classification sources

- **[InEKData2025]** InEK GmbH. Unterjährige Datenlieferung DRG Januar bis Dezember 2025, data delivery January 16, 2026, classifications 2025. [Data browser](https://datenbrowser.inek.org/DRG202601).
- **[InEKManual2026]** InEK GmbH. InEK DatenBrowser user manual, version September 1, 2026; dataset section 2.51. [Manual](https://datenbrowser.inek.org/assets/manual/InekDatenBrowser.pdf).
- **[BfArMOPS2025]** BfArM. OPS 2025, neurological complex treatment codes 8-981 and 8-98b. [Official classification](https://klassifikationen.bfarm.de/ops/kode-suche/htmlops2025/block-8-97...8-98.htm).
- **[BfArMR132025]** BfArM. ICD-10-GM 2025, R13 dysphagia. [Official classification](https://klassifikationen.bfarm.de/icd-10-gm/kode-suche/htmlgm2025/block-r10-r19.htm).
- **[BfArMU692025]** BfArM. ICD-10-GM 2025, U69 pneumonia-timing codes. [Official classification](https://klassifikationen.bfarm.de/icd-10-gm/kode-suche/htmlgm2025/block-u69-u69.htm).

- **[InEKPCCL2025]** InEK GmbH. Abschlussbericht zur Weiterentwicklung des aG-DRG-Systems fuer das Jahr 2025. December 19, 2024. Section 3.3.1.4, CCL matrix and PCCL. [Official report](https://www.g-drg.de/content/download/14761/file/Abschlussbericht_aG-DRG_2025_2024-12-19.pdf).
- **[BfArMFunction2025]** BfArM. ICD-10-GM 2025, U50-U52 functional impairment codes and assessment timing. [Official classification](https://klassifikationen.bfarm.de/icd-10-gm/kode-suche/htmlgm2025/block-u50-u52.htm).
- **[BfArMBarthel2025]** BfArM. ICD-10-GM 2025, Barthel Index criteria according to the Hamburg Manual. [Official scoring criteria](https://klassifikationen.bfarm.de/icd-10-gm/kode-suche/htmlgm2025/zusatz-06-anh-barthelindex.htm).

The initial literature and coding sources were accessed November 16, 2026; additional coding sources and the author-specific PubMed update were verified November 17, 2026.

