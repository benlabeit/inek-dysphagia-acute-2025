# Historical binary analyses within diagnosis-related groups

The current adult-only analysis covers all 16 binary endpoints and uses pooled reference weights. See the [current manuscript and results](README.md#current-adult-cohort-analysis-18-november-2026). The material below documents the earlier comparison using dysphagia-group weights.

The manuscript reports the adult case-mix comparisons in Tables S15 and S16 and the ranges compatible with marginal counts in Table S17. These post hoc analyses use German 2025 acute stroke-care episodes with and without secondary dysphagia coding. The 75-year boundary separates two adult age strata. The all-age analyses also include children.

## Computation

Run `python outcomes_within_drg.py --raw /path/to/native_exports --output /path/to/results` from the repository. The script reads the current published crude outcome list for its endpoint definitions and checks the native workbook delivery, filters, integer DRG counts and group nesting. It reads case counts from the DRG distribution. It never assigns a pooled residual row to an individual DRG. The script does not access the DatenBrowser.

For each eligible stratum, the comparator denominator and event count are the counts in all episodes minus those in episodes coded for dysphagia. Both denominators must be positive. A directly determined zero is valid. An absent row remains unknown. For adult pneumonia in the 18–74 all-diagnosis stratum, the unrestricted event workbooks contain zero minors. A DRG-specific younger count can therefore be obtained by subtracting the directly observed older count from the unrestricted count when both rows exist. For residual principal diagnoses, all three contributing sources must have the required named DRG.

With D dysphagia episodes, C comparators, dₖ and cₖ cases and aₖ and bₖ events in stratum k, let wₖ = dₖ / Σdₖ over eligible strata. Standardized risks are Σwₖ aₖ/dₖ and Σwₖ bₖ/cₖ. Each crude RR uses precisely the same included cases. The independent-binomial variance of each standardized risk is Σwₖ²pₖ(1−pₖ)/nₖ. We use fixed-weight delta intervals on the log-RR scale and the risk-difference scale. These nominal intervals condition on the reported cells and group weights. Zero-event or all-event strata can produce optimistic precision. Risk differences in the CSV files are proportions and are multiplied by 100 for percentage points.

- **All-age DRG.** Direct unrestricted event-filtered sources were available for death, pneumonia and the malnutrition union. The all-age mortality sensitivity omits B70G and B70H if present. Only B70G entered the full mortality comparison. Both groups incorporate early death in the 2025 classification. [InEK catalogue](https://www.g-drg.de/content/download/14155/file/Fallpauschalenkatalog%202025_2024-09-26.pdf)
- **Adult DRG and adult age × DRG.** These use the same outcome-specific adult cases. Eligible age-by-DRG cells are pooled across age within each DRG for the DRG-only estimate. For the age-adjusted estimate they remain separate.
- **Adult age × principal diagnosis × DRG.** Age bands are 18–74 and ≥75 years. Diagnosis strata are I63, I61 and all remaining principal diagnoses. This finer model has its own eligible cases. Coverage is reported separately for each exposure group.
- **Reference population.** All DRG models follow the dysphagia-group weighting used for length of stay. The age–diagnosis models without DRG use pooled weights. Comparisons across models with different eligible cells or reference weights are descriptive.
- **Additional covariates.** The demographic sex and PCCL distributions do not supply joint DRG event counts. DRGs can reflect clinical course, complications and procedures. The comparisons cannot isolate a causal effect or adjust for admission NIHSS.

## Endpoints with marginal event counts

For an endpoint without joint event counts, the denominator support is defined independently of the event. Within each exposure group and available age or age–diagnosis block, assign each event to a known DRG or to the block's excluded cases. Every assignment respects the observed event margin and the capacity of each group. Each included event contributes wₖ/nₖ to the standardized risk. An excluded event contributes zero. Allocating the fixed event total in ascending or descending order of contribution gives the respective limiting risk. Combine the group-specific extrema to obtain RR and RD limits. The limits use only the indicated margins and denominators. They carry no confidence level. When zero comparator risk is possible, the RR has no finite upper limit. Sparse missing diagnosis margins precluded the six-block adult bounds for E44.0 and E44.1.

## Files

- [Observed estimates, matched crude RRs, risks, differences, coverage and sparsity](within_drg_binary_estimates.csv)
- [Ranges compatible with the observed margins](within_drg_binary_bounds.csv)
- [Point-estimate availability across all 16 endpoints](within_drg_binary_availability.csv)
- [Manual source export list](within_drg_manual_exports.csv)

The list identifies 20 unrestricted workbooks for the ten endpoints currently lacking point estimates. For those same ten endpoints, a further 40 age-specific exports support age comparisons and 80 age-by-diagnosis exports complete the requested source grid before disclosure suppression. The twelve restricted E43 selections had previously supported the non-DRG models. Reusing those original workbooks would supply their DRG sheets. The final six optional all-age queries cover three endpoints already analyzed in adults. More files can supply more identifiable DRG counts, but the number of reportable rows depends on source disclosure. Retain the full native workbooks locally.

All selections use the 16 acute OPS codes (8-981 and 8-98b with suffixes .20–.23 and .30–.33) and the same interim January–December 2025 delivery. The dysphagia group adds R13.0, R13.1 or R13.9 as secondary diagnoses. Add the outcome as a separate AND filter with the acute cohort, using the further secondary-diagnosis or further-procedure selector as applicable. A procedure endpoint must never be OR-ed into the acute cohort definition.
