# Draft Dysphagia and inpatient burden in German acute stroke care

# Abstract

**Background:** Dysphagia is associated with adverse stroke outcomes, but its nationwide inpatient burden is difficult to separate from neurological severity and case mix.

**Methods:** We analyzed aggregate InEK January-December 2025 data for hospital episodes receiving OPS-defined neurological complex treatment of acute stroke. Dysphagia was defined by R13.0, R13.1 or R13.9 secondary diagnoses. Outcomes included length of stay, unique-case pneumonia coding and inpatient death. Exploratory analyses compared stays within diagnosis-related groups (DRGs), standardized mortality by age and outcomes by patient clinical complexity level (PCCL), and examined diagnosis and functional subgroups.

**Results:** Among 279,277 episodes, 33,643 (12.05%) had dysphagia coding. Mean stay was 16.26 versus 7.41 days; the within-DRG difference was 3.61 days (95% confidence interval [CI] 3.45-3.78), covering 98.28% of dysphagia episodes. The combined J12-J18 or J69.0 pulmonary endpoint occurred in 33.22% versus 4.57% (risk ratio [RR] 7.27, 95% CI 7.10-7.44). Mortality was 14.87% versus 3.15% (RR 4.72, 95% CI 4.56-4.88); separate age and PCCL standardizations yielded RRs of 4.08 (95% CI 3.95-4.23) and 3.20 (95% CI 3.07-3.33). The PCCL-standardized J12-J18 pneumonia RR was 2.07 (95% CI 1.97-2.16). Functional-category mortality contrasts varied: RR 1.08 (95% CI 1.03-1.15) at Barthel Index 0-15 and 1.02 (95% CI 0.90-1.15) at extended Barthel Index 0-15.

**Conclusions:** Recorded dysphagia identifies substantial pulmonary morbidity, mortality and resource use. Associations persisted after separate administrative standardizations but varied within functional subgroups. Selective coding and residual neurological-severity confounding preclude claims of independent causal effects or preventable burden.

**Keywords:** dysphagia; stroke; administrative data; pneumonia; length of stay; FEES; Germany

# Introduction

Dysphagia affects the safety and efficiency of swallowing and can complicate acute stroke care through aspiration, inadequate intake and difficulty administering medication. It also influences feeding decisions and discharge planning. European guidance consequently places early swallowing screening and structured assessment within routine stroke management [Dziewas2021Guideline]. Yet estimates of its frequency depend strongly on case selection, assessment method and timing. Arnold and colleagues identified dysphagia in 20.7% of consecutively treated patients with ischemic stroke using the Gugging Swallowing Screen [Arnold2016]. In the more recent Swedish DESIRE cohort, standardized assessment within 96 hours identified dysphagia in 38.8% of 1,093 patients [Selg2026]. Administrative coding therefore captures a different phenotype from prospectively assessed swallowing impairment.

The clinical significance of dysphagia extends beyond its frequency. In a German multicentre cohort of 12,276 patients with acute ischemic stroke, dysphagia was associated with pneumonia, inpatient death and disability after adjustment for measured clinical variables [AlKhaled2016]. A substantially larger German registry documented persistent associations with adverse outcomes over eight years despite increasing screening and speech-language therapy coverage [SuntrupKrueger2018]. These observations support a continuing need to quantify the burden encountered by contemporary stroke services. They do not imply that all outcome differences are directly caused by swallowing dysfunction, because age, stroke severity and disability affect both dysphagia and prognosis.

Resource implications are similarly relevant. A German FEES-based study found that severe dysphagia with impaired secretion management was associated with higher acute hospitalization expenditure from the health-insurance perspective [Labeit2023Costs]. US Medicare and Spanish hospital studies also identified economic differences, although the time horizon, diagnostic definitions and costing methods differed [Bonilha2014; Marin2021]. National hospital data can complement these clinical studies by describing case volume and occupied bed-days across a broad range of providers. Such data cannot convert an association with longer hospitalization into an estimate of avoidable costs without additional causal and economic assumptions.

Germany's InEK database has already been used to describe FEES implementation. Ungerer and colleagues analyzed 1,540,947 stroke-unit episodes from 2019 to 2024, documenting variation in FEES coding across years and institutional service levels [Ungerer2026]. A further nationwide analysis is therefore most useful when it addresses the burden accompanying documented dysphagia rather than claiming novelty for national FEES frequencies alone. International administrative studies also illustrate the importance of interpretation: a US analysis found longer stays but lower adjusted inpatient mortality among patients with coded dysphagia, emphasizing the sensitivity of administrative associations to ascertainment and selection [Vasan2023].

We examined the association of an R13 secondary diagnosis with respiratory diagnoses, inpatient death, FEES use and length of stay in the 2025 InEK acute stroke-care cohort. We additionally distinguished overlapping pneumonia codes, described coded dysphagia in clinically relevant treatment and diagnosis subgroups, compared length of stay within DRGs, and examined whether outcome contrasts persisted within documented functional categories and after PCCL standardization. The objective was to quantify the nationwide burden associated with recorded dysphagia while keeping the limits of aggregated administrative information explicit.

# Methods

## Design and data source

This retrospective observational study used aggregate hospital data from the InEK DatenBrowser release “Unterjährige Datenlieferung DRG Januar bis Dezember 2025,” with the delivery dated January 16, 2026 and the 2025 diagnostic, procedure and DRG classifications. This release was retained to reproduce the source analyses; it is distinct from the subsequent annual 2025 delivery grouped using 2026 DRGs. Results therefore refer to the selected release and may differ after later submissions or regrouping. Source exports and analysis scripts were retained for reproducibility. The unit was a hospital episode, not an identifiable person. Repeated admissions and transfers could not be linked. The reporting approach was informed by STROBE and RECORD [vonElm2007STROBE; Benchimol2015RECORD; InEKData2025; InEKManual2026].

## Care cohort and dysphagia definition

Eligible episodes had at least one of the following OPS codes: 8-981.20, .21, .22, .23, .30, .31, .32 or .33; or 8-98b.20, .21, .22, .23, .30, .31, .32 or .33. These codes identify neurological complex treatment for acute stroke care of at least 24 hours. Their coding rules also permit transient ischemic attack and ischemia in the ophthalmic arterial territory. The cohort was consequently defined by care provision rather than a principal diagnosis of stroke. No adult-only restriction was applied to the main analysis [BfArMOPS2025].

The exposed group comprised episodes with any secondary diagnosis R13.0, R13.1 or R13.9. These codes describe dysphagia requiring supervision during eating, dysphagia in a specified tracheostomy context, and other or unspecified dysphagia, respectively [BfArMR132025]. They were combined as a union. The comparator comprised episodes without these R13 secondary diagnoses. This definition does not establish normal swallowing and does not exclude dysphagia recorded solely as a principal diagnosis. The data did not identify onset, persistence, cause or directly measured severity of swallowing impairment.

## Outcomes and additional analyses

The main burden measures were hospital length of stay and the J69.0 secondary diagnosis, operationally termed an aspiration-related pneumonitis/pneumonia coding. We also examined the union of J12–J18 secondary diagnoses and its combination with J69.0. The two code groups were allowed to overlap; they were not treated as mutually exclusive diagnoses. In-hospital death was obtained from the discharge-status query.

Additional descriptive measures included volume depletion (E86), hypoxemic acute respiratory failure (J96.00), selected malnutrition diagnoses, and pneumonia-timing codes U69.01 and U69.04. U69.01 identifies pneumonia occurring more than 48 hours after admission; U69.04 identifies pneumonia present at admission or arising within 48 hours. These timing codes are specified for fully inpatient adults and do not establish timing relative to dysphagia or stroke onset. They need not be mutually exclusive at the episode level [BfArMU692025].

FEES was identified using OPS 1-613. Intracranial mechanical thrombectomy was identified using OPS 8-836.80; device-material codes were not substituted for the procedure definition. Dysphagia frequency was described within the thrombectomy subgroup and principal-diagnosis groups for cerebral infarction (I63) and intracerebral hemorrhage (I61). These subgroup frequencies were descriptive and were not interpreted as treatment effects. Endpoints and sensitivity analyses were selected during retrospective replication and expansion of the presentations; the study was not preregistered.

## Extraction and quality checks

For diagnoses and procedures, we used the export field “Fälle,” representing episodes with a code, rather than “Nennungen,” representing code mentions. Direct union queries were used for multicode pneumonia endpoints because summing individual code counts can count one episode repeatedly. Comparison-group counts were obtained by subtracting the dysphagia subgroup from the identically defined total cohort. Stored full-precision proportions were converted to counts only when they resolved to integers within numerical tolerance. Suppressed or omitted small cells were not assigned zero.

Counts, cohort filters and totals were reconciled across exports. Length-of-stay reconstruction used the means and second moments for the total and dysphagia groups. Internal checks of second moments for integer-valued lengths of stay supported a sample-standard-deviation convention for the overall “Info” exports and a population-standard-deviation convention for DRG rows. This was an empirical finding from the exports, not an assumed official specification; each convention was converted consistently before calculating uncertainty.

## Statistical analysis

We report proportions, unadjusted risk ratios and risk differences. Proportion intervals used the Wilson method; risk-ratio intervals used the log-Wald method. Mean length-of-stay differences used a normal approximation with separate group variances. The comparator mean and variance were recovered by subtracting the dysphagia group's first and second moments from the corresponding total-cohort moments.

For DRGs with estimable values in both groups, we calculated the within-DRG mean difference and weighted it by the number of episodes with dysphagia in that DRG. Thus, the comparison was standardized to the observed DRG distribution of the dysphagia subgroup. A sensitivity analysis required at least 20 episodes in each group per DRG. Associated bed-days were calculated as the sum of each within-DRG difference multiplied by its dysphagia count. This descriptive quantity is not an attributable or preventable burden estimate.

For exploratory age-standardized mortality, we reconstructed deaths and denominators in three bands: under 65, 65-79 and 80 years or older. Group-specific risks were directly standardized to the pooled age distribution of all 279,277 selected episodes, with weights 24.196%, 36.477% and 39.327%, respectively. The under-65 band included the 22 episodes aged under 18. Confidence intervals for the standardized risk difference and log risk ratio used the delta method with fixed observed weights and independent binomial variances. This comparison addresses broad age composition only; residual differences within bands and other confounding remain. Mortality within principal-diagnosis I61 was reconstructed only after confirming that every expected endcode was present in all four relevant exports. Because I63.6 was omitted from the death tables, an exact cerebral-infarction sensitivity cohort was explicitly restricted to the eight endcodes I63.0-I63.5, I63.8 and I63.9. It was not labeled the full I63 group. Main-diagnosis categories are mutually exclusive, permitting sums of complete endcode sets. These restrictions address diagnostic composition, not severity within a diagnosis.

For PCCL-standardized mortality and J12-J18 pneumonia, the seven PCCL categories (0-6) were confirmed to be exhaustive and mutually exclusive in the total, dysphagia and corresponding outcome-filtered exports. Both exposure groups were represented in every stratum. Group-specific risks were directly standardized to the PCCL distribution of the entire care cohort; intervals used the same fixed-weight binomial delta method as the age analysis. Age and PCCL standardizations were separate analyses. PCCL summarizes the resource-related contribution of coded complications and comorbidities and is not an admission neurological score [InEKPCCL2025]. It can include diagnoses on pathways between dysphagia and outcomes. Consequently, this standardization is descriptive rather than an estimate of a baseline-severity-adjusted causal effect.

Functional sensitivities compared mortality and J12-J18 pneumonia within each of 21 ICD-10-GM categories representing the Barthel Index, motor Functional Independence Measure (FIM), extended Barthel Index, cognitive FIM and Mini-Mental State Examination (MMSE). Instruments were analyzed separately. The 2025 U50/U51 rules specify assessment during the first five hospital days, or at the beginning of geriatric or early-rehabilitation care, and the highest score within that window when values change [BfArMFunction2025]. Thus, these codes are temporally defined proxies rather than proven pre-dysphagia measurements. The Barthel Index includes eating or PEG self-care, preventing its interpretation as entirely independent of swallowing-related care [BfArMBarthel2025]. Each individual-code analysis required explicit denominator and outcome rows in all four relevant exports. Missing rows were retained as non-estimable rather than zero. All candidate categories and their availability are reported in Supplementary Tables S1-S2. We did not add code counts to infer unique test coverage, combine instruments into one scale, or calculate a multi-category functional standardization without verified episode-level exclusivity. A code-absent group does not indicate normal function. These analyses were developed after inspection of the initial results and remain exploratory.

We also subtracted the death cohorts' counts, sums and second moments from their corresponding total cohorts to derive length of stay among episodes ending in discharge alive. Overall reconstruction used the Info sample-SD convention. Survivor DRG reconstruction used population-SD moments and required an explicitly displayed death row in both the total and dysphagia exports; an absent row could contain suppressed cases and was not treated as zero. The resulting restricted within-DRG comparison was weighted to the included dysphagia-survivor distribution, with coverage reported. These analyses condition on survival and are descriptive sensitivity analyses, not estimates free of mortality-related selection.

The nationwide delivery is not a random sample. The intervals are model-based summaries conditional on the observed data and, for the DRG analysis, the observed weights. They assume independent episodes and do not account for hospital clustering, repeat admissions, coding error or residual confounding. No patient-level records or admission NIHSS measurements were available. Separate marginal standardizations must not be interpreted as simultaneous adjustment for age, sex, principal diagnosis, functional status and PCCL. Multiple comparisons were considered exploratory; interpretation emphasized magnitude, consistency and clinical context rather than significance thresholds.

## Literature context and research governance

A targeted narrative literature search was conducted on November 16, 2026 using web searches to retrieve primary PubMed records, publisher pages and publicly available full texts, supplemented by reference-list inspection. The search covered dysphagia ascertainment, pneumonia, mortality, hospital stay, costs, FEES and interventions, with emphasis on German and nationwide evidence. It was not a systematic review or meta-analysis; the search appendix records the queries and limits.

The analysis used anonymous aggregate information and did not involve participant contact or access to patient identifiers. The authors must confirm the applicable institutional ethics determination, data-use requirements, funding, conflicts of interest and contributor details before submission. No approval, waiver or declaration is assumed here.

# Results

## Cohort and documented dysphagia

The cohort contained 279,277 hospital episodes (Table 1). An R13 secondary diagnosis was present in 33,643 episodes (12.05%, 95% CI 11.93–12.17), leaving 245,634 episodes in the comparator group. Principal diagnoses were heterogeneous: 176,029 episodes had cerebral infarction and 12,148 had intracerebral hemorrhage. Dysphagia was documented in 26,613 (15.12%) and 3,364 (27.69%), respectively. The displayed G45 principal-diagnosis rows contained 75,056 episodes, demonstrating the substantial contribution of transient ischemic and related syndromes to the care-defined denominator. Small-cell suppression prevents treating every displayed category sum as a fully verified union.

Intracranial thrombectomy was recorded in 19,553 episodes, of which 6,448 (32.98%) had an R13 secondary diagnosis. Among the remaining 259,724 episodes, 27,195 (10.47%) had an R13 secondary diagnosis, corresponding to an unadjusted RR of 3.15 (95% CI 3.08–3.22).

## Pulmonary diagnoses and death

Aspiration-related pneumonitis/pneumonia codes occurred in 7,801 episodes with dysphagia and 4,444 comparator episodes. The unique J12–J18 union comprised 3,875 and 7,026 episodes, respectively. J69.0 and J12–J18 co-occurred in 501 and 241 episodes. Accounting for this overlap, the combined endpoint affected 11,175 episodes with dysphagia (33.22%) and 11,229 comparator episodes (4.57%). Direct union counts were lower than the sums of individual J12–J18 rows, which were 4,240 and 7,340, respectively.

There were 5,003 inpatient deaths among episodes with dysphagia and 7,746 among comparator episodes, yielding mortality proportions of 14.87% and 3.15%. Volume depletion and both pneumonia-timing markers were also more frequent in episodes with dysphagia. Table 2 presents the principal coded outcomes; Table 3 separates the overlapping pulmonary categories.

After direct standardization to the cohort's three-band age distribution, mortality was 13.1696% with an R13 secondary diagnosis and 3.22435% without one (RR 4.08, 95% CI 3.95-4.23; risk difference 9.95 percentage points, 95% CI 9.59-10.30). Age-specific RRs were 4.83 below age 65, 4.82 at ages 65-79 and 3.69 at age 80 or older (Table 5). These age-specific and standardized estimates describe broad age composition without controlling neurological severity.

## Diagnosis and functional severity sensitivities

After standardization to the pooled PCCL distribution, mortality was 11.47% with an R13 secondary diagnosis and 3.59% without one (RR 3.20, 95% CI 3.07-3.33; risk difference 7.88 percentage points, 95% CI 7.48-8.28). PCCL-standardized J12-J18 pneumonia risks were 6.99% and 3.39% (RR 2.07, 95% CI 1.97-2.16; risk difference 3.61 percentage points, 95% CI 3.32-3.90). The mortality association varied across PCCL categories, with RRs of 6.91 at PCCL 0, 2.01 at PCCL 3 and 1.14 at PCCL 4; the standardized contrast does not imply a uniform stratum-specific association.

The exactly observed cerebral-infarction sensitivity cohort excluding I63.6 comprised 175,955 episodes. Mortality was 3,871/26,604 with dysphagia and 5,556/149,351 without dysphagia (14.55% versus 3.72%; RR 3.91, 95% CI 3.76-4.07). Within the complete I61 subgroup, mortality was 611/3,364 versus 1,084/8,784 (18.16% versus 12.34%; RR 1.47, 95% CI 1.34-1.61). These different contrasts demonstrate the relevance of diagnostic composition but do not control severity within each diagnosis (Table 6).

Functional-category associations were heterogeneous. Within Barthel Index 0-15 (U50.50), mortality was 1,894/9,215 versus 2,244/11,843 (20.55% versus 18.95%; RR 1.08, 95% CI 1.03-1.15), whereas the J12-J18 pneumonia RR was 1.32 (95% CI 1.23-1.42). Within extended Barthel Index 0-15 (U51.20), mortality was 334/1,093 versus 400/1,332 (30.56% versus 30.03%; RR 1.02, 95% CI 0.90-1.15); the pneumonia RR was 1.47 (95% CI 1.20-1.79). Mortality RRs in less impaired Barthel categories ranged from 2.42 at 20-35 points to 31.88 at 100 points, with substantial differences in baseline risks and subgroup sizes (Supplementary Tables S1-S2). These selected groups must not be compared with the full-cohort crude RR as a decomposition of confounding.

Exact comparisons were available for 31 of 42 category-by-outcome combinations; the remaining 11 were not estimable because required rows were absent. Coding was incomplete: even the sum of all six displayed Barthel category counts covered only 41.11% of the full cohort, an upper bound on unique coverage rather than a verified union. Consequently, the functional analyses describe episodes with particular recorded assessments, not a severity adjustment of the complete cohort.

## Length of stay and FEES

Mean hospital stay was 16.26 days in the dysphagia group and 7.41 days in the comparator group. The unadjusted difference was 8.85 days (95% CI 8.67–9.04). Within-DRG comparisons covered 171 DRGs and 33,063 episodes with dysphagia, representing 98.28% of the exposed group. The weighted difference was 3.61 days (95% CI 3.45–3.78), corresponding to 119,423 associated bed-days within the included strata. Requiring at least 20 episodes in each group retained 59 DRGs and 95.43% of the dysphagia group; the difference remained 3.60 days (Table 4).

Among episodes ending in discharge alive, 28,640 episodes with dysphagia had a mean stay of 16.72 days (sample SD 17.63), compared with 7.32 days (sample SD 6.97) in 237,888 comparator episodes. The difference was 9.40 days (95% CI 9.19-9.60). The restricted survivor DRG analysis included 58 DRGs and 27,222 episodes with dysphagia, covering 95.05% of dysphagia survivors, and yielded a difference of 3.59 days (95% CI 3.41-3.78; Table 5). Omitted death rows prevented exact reconstruction of the remaining DRGs.

FEES was coded in 6,776 episodes with dysphagia (20.14%) and 2,182 comparator episodes (0.89%). Overall, 8,958 episodes had FEES coding, or 3.21% of the care cohort. These frequencies describe coded use and do not identify the proportion with a clinical indication for instrumental assessment.

# Discussion

This analysis identified a large concentration of inpatient burden among hospital episodes with an R13 secondary diagnosis in German acute stroke care. Approximately one in eight episodes had documented dysphagia. These episodes accounted for markedly higher proportions of pulmonary diagnoses and inpatient death and had a mean stay more than twice that of the comparator group. A substantial length-of-stay difference persisted within DRGs, and mortality and pneumonia contrasts persisted after PCCL standardization. However, associations varied materially across diagnostic and functional subgroups, including a near-null mortality contrast in the most impaired extended-Barthel group. The findings establish the scale of recorded burden while leaving the causal contribution of dysphagia unresolved.

## Coding frequency and clinical dysphagia are different measures

The 12.05% coding frequency should not be interpreted as the clinical prevalence of post-stroke dysphagia. First, the denominator includes a substantial number of transient ischemic and related syndromes. Restriction to principal cerebral infarction or intracerebral hemorrhage increased the observed frequency to 15.12% and 27.69%, respectively. Second, coding depends on recognition, documentation and local practice. Prospective clinical cohorts have generally identified more swallowing impairment, including the recent DESIRE study using standardized screening [Arnold2016; Selg2026]. These differences are compatible with incomplete ascertainment of milder or transient dysfunction but cannot quantify its extent.

The exposure also combines clinically different conditions. An unspecified R13 diagnosis, need for supervision during eating and dysphagia in a tracheostomy context are not interchangeable levels on a validated severity scale. An exploratory US administrative severity framework has recently been proposed, but its authors emphasized the need for validation [Horn2026]. It cannot simply be transferred to German aggregate data. Future work should link administrative coding to standardized clinical assessment and swallowing trajectories, including recovery of oral intake [Galovic2019].

## Respiratory burden and mortality

The largest relative contrast concerned J69.0. This association is clinically plausible and consistent with German clinical cohorts linking dysphagia to pneumonia [AlKhaled2016; SuntrupKrueger2018]. J69.0 encompasses aspiration-related pneumonitis as well as pneumonia and should not be equated with clinically confirmed bacterial infection. The code does not provide direct evidence of aspiration on swallowing assessment, microbiology or standardized pneumonia adjudication. The combined endpoint showed that pulmonary morbidity remained prominent when the analysis included J12–J18 and accounted for dual coding. Explicitly constructing these unions is important: adding diagnosis rows would overstate the number of affected episodes and alter the estimated contrast.

Pneumonia-timing markers add a useful descriptive distinction. Both early and later documented pneumonia were substantially more common in the dysphagia group. Nevertheless, a diagnosis after 48 hours of admission is not necessarily an event after dysphagia onset, and a longer hospital stay creates more opportunity for later pneumonia and its detection. The present data therefore cannot determine the sequence of swallowing impairment, respiratory deterioration and prolonged hospitalization. Nor do admission-based U69 markers reproduce the PISCES definition of stroke-associated pneumonia within seven days of stroke onset [Smith2015PISCES]. They should not be used to infer preventable hospital harm.

The higher inpatient mortality is consistent with several clinical studies, but administrative associations are not uniform. Vasan and colleagues found lower adjusted inpatient mortality associated with coded dysphagia in US ischemic and hemorrhagic stroke admissions despite longer stays [Vasan2023]. This contrast reinforces the possibility of differences in case selection, documentation and survival time available for diagnosis. The present cohort also requires at least 24 hours of qualifying complex treatment, potentially excluding very early deaths and short episodes. More severe neurological injury, frailty, pre-existing swallowing disorders and limitations of treatment may contribute to the observed mortality difference. Without these variables, an independent mortality effect cannot be estimated.

Volume depletion was also more frequent with dysphagia, but E86 is not a validated dysphagia-specific dehydration phenotype. It can precede hospitalization or reflect other disease processes. Likewise, malnutrition and respiratory failure codes are useful burden markers without resolving their temporal or causal relationship to swallowing dysfunction. Longitudinal studies have demonstrated that clinically important consequences may extend beyond discharge, although their definitions and follow-up differ from the current study [Ho2018].

## Interpreting the severity analyses

The additional analyses address different aspects of case mix. Restriction to cerebral infarction reduces the influence of transient ischemic syndromes in the broad care cohort, while separate I61 results show that the same dysphagia code can identify different relative risks across diagnoses. PCCL standardization demonstrates that the overall contrasts are not explained solely by unequal distributions of this administrative complexity measure. It does not establish independence from neurological injury: PCCL is influenced by diagnoses accumulated during the episode, including potential complications and consequences of swallowing impairment. Conditioning on such variables may remove mediated associations or create selection bias.

The functional sensitivities add clinical context because their coding rules specify an early assessment window. Nevertheless, early assessment is not necessarily before dysphagia, the recorded categories are broad, and test availability is selective. The near-null mortality association within extended Barthel Index 0-15 and the much smaller contrast within Barthel Index 0-15 indicate that the full-cohort RR is not a generalizable effect across functional states. Conversely, the persistence of pneumonia contrasts in these groups is compatible with clinically relevant swallowing-related burden, but remains vulnerable to residual confounding and ascertainment. These observations do not prove a causal interaction, a protective effect in any group, or a percentage of risk explained by severity. Differences between instruments also cannot be used to rank their confounding control, because they select different episodes. Admission NIHSS, premorbid disability, lesion characteristics, treatment limitations and swallowing-onset times would be needed to more directly address neurological baseline severity.

## Hospital stay and resource implications

The length-of-stay findings provide a practical measure of service burden. The contrast was descriptively attenuated from 8.85 days overall to 3.61 days when comparisons were made within DRGs and weighted to the dysphagia distribution. These estimates concern different comparisons; their difference does not decompose the crude association into causal components. The within-DRG difference was stable when small DRG strata were excluded and remained apparent in the restricted analysis of episodes ending in discharge alive. This supports the descriptive finding that episodes with recorded dysphagia consume more inpatient time within the same payment categories, while conditioning on discharge alive introduces an additional selection constraint.

DRG stratification is not equivalent to adjustment for baseline clinical severity. DRGs incorporate diagnoses, complications and treatments that may themselves be affected by dysphagia or its consequences. Conditioning on these variables can remove mediated effects or introduce selection bias. Consequently, neither the crude nor the within-DRG estimate should be labeled the causal prolongation attributable to dysphagia. The associated bed-day quantity expresses the observed contrast at the size of the exposed population; it does not represent bed-days that would disappear following an intervention.

The findings complement the FEES-based German expenditure study, which identified particularly severe dysphagia as a marker of higher insurer spending [Labeit2023Costs]. They are also consistent with the wider economic literature [Bonilha2014; Marin2021]. Nonetheless, bed occupancy, reimbursement, accounting costs and societal costs are distinct quantities. Applying a fixed daily price to the current difference would require explicit assumptions and would not produce a valid estimate of savings or cost effectiveness.

## Assessment and management

FEES was coded in roughly one fifth of episodes with dysphagia. The national FEES study by Ungerer and colleagues provides the direct historical context for this observation [Ungerer2026]. The current overall frequency is close to their reported 2024 value, but a temporal comparison requires harmonized data releases, cohort definitions and coding. This single-year analysis does not test the effect of certification standards or a change in clinical practice.

A low FEES proportion alone does not establish undertreatment. Clinical screening and bedside assessment may answer some questions, swallowing may recover, alternative instrumental methods may be used, and goals of care may limit investigations. Conversely, the multicentre FEES registry and stroke-specific studies show that instrumental assessment often informs feeding decisions [Dziewas2019Registry; Braun2019]. The relevant quality question is whether assessment is timely and appropriate for the patient's swallowing risk, rather than whether every episode with an R13 code contains a FEES code.

The thrombectomy subgroup had a particularly high coding frequency. A clinical cohort using early FEES regardless of screening results found dysphagia in 81% of thrombectomy-treated patients, illustrating how ascertainment and selection affect the reported proportion [Pinho2024]. Our comparison with episodes without thrombectomy is confounded by stroke severity and by inclusion of transient ischemic syndromes in the latter group. It should not be interpreted as a harmful effect of reperfusion treatment.

Evidence supporting better dysphagia pathways comes from designs that examine care processes and interventions directly. Formal-screening studies, a quality-improvement time series and a large national audit linked structured or earlier assessment with fewer respiratory complications [Hinchey2005; Titsworth2013; Bray2017]. The Austrian stroke registry also reported associations between dysphagia management and lower mortality in more severely affected patients [Hotz2025]. QASC demonstrated benefit from a combined fever, glucose and swallowing protocol, although the swallowing component cannot be isolated [Middleton2011QASC]. Feeding and rehabilitation decisions likewise require intervention-specific evidence: FOOD does not support routine early PEG, and PHAST-TRAC evaluated stimulation in a selected tracheotomized population [Dennis2005FOOD; Dziewas2018PHAST]. None of these treatment effects can be inferred from the present aggregate procedure frequencies.

## Strengths and limitations

The principal strengths are national coverage of the defined care pathway, transparent code-based selection, reconstruction from original exports, direct handling of overlapping outcomes, and sensitivity analysis of hospital stay. Important limitations are absence of admission NIHSS, premorbid disability and patient-level functional measurements; selective availability of broad functional coding categories; incomplete clinical ascertainment; lack of onset times; inability to link patients or model hospital clustering; small-cell suppression; and reliance on a specific interim data release. The very narrow model-based intervals do not encompass these uncertainties. All associations are exploratory and descriptive. A companion analysis of neurological and neurosurgical early rehabilitation uses the same source and may include overlapping episodes; it is not an independent replication, and the two cohorts cannot be interpreted as linked stages of individual recovery.

A useful next step is validation of these diagnostic and functional sensitivities against admission clinical measurements and harmonized multiyear analyses, including explicitly defined adult-only cohorts. Studies assessing service improvement should measure time to screening, indication and timing of FEES, nutrition, functional recovery and clinically adjudicated pulmonary outcomes. Such work can determine which elements of the observed burden are modifiable.

# Conclusion

An R13 secondary diagnosis identified a substantial burden of pulmonary morbidity, inpatient mortality and prolonged hospitalization in the German OPS-defined acute stroke-care cohort. PCCL-standardized outcome contrasts and the within-DRG length-of-stay difference support its relevance as a marker of inpatient care burden. Functional subgroup results show that the association is not uniform across documented impairment levels. The findings support systematic swallowing assessment and management without quantifying effects independent of neurological baseline severity, preventable events or savings.

# Tables

## Table 1 Selected characteristics of the acute stroke care cohort

| Characteristic | R13 secondary diagnosis n = 33,643 | No R13 secondary diagnosis n = 245,634 |
| --- | ---: | ---: |
| Age under 65 years | 4,756 (14.14%) | 62,818 (25.57%) |
| Age 65–79 years | 11,240 (33.41%) | 90,633 (36.90%) |
| Age 80 years or older | 17,647 (52.45%) | 92,183 (37.53%) |
| Male | 17,552 (52.17%) | 129,189 (52.59%) |
| Female | 16,091 (47.83%) | 116,438 (47.40%) |
| Principal diagnosis I63 cerebral infarction | 26,613 (79.10%) | 149,416 (60.83%) |
| Principal diagnosis I61 intracerebral hemorrhage | 3,364 (10.00%) | 8,784 (3.58%) |
| Intracranial thrombectomy OPS 8-836.80 | 6,448 (19.17%) | 13,105 (5.34%) |
| FEES OPS 1-613 | 6,776 (20.14%) | 2,182 (0.89%) |

Values are episode counts and within-column percentages. The age bands are exhaustive; the displayed principal-diagnosis categories are selected and do not exhaust the cohort. Treatment rows can overlap diagnosis rows. Group membership denotes R13 secondary-diagnosis coding, not clinically confirmed presence or absence of swallowing impairment.

## Table 2 Coded outcomes

| Endpoint | R13 secondary diagnosis n = 33,643 | No R13 secondary diagnosis n = 245,634 | Unadjusted RR with 95% CI |
| --- | ---: | ---: | ---: |
| Aspiration-related pneumonitis/pneumonia J69.0 | 7,801 (23.19%) | 4,444 (1.81%) | 12.82 (12.38–13.27) |
| Pneumonia J12–J18 unique union | 3,875 (11.52%) | 7,026 (2.86%) | 4.03 (3.88–4.18) |
| Pneumonia or aspiration-related pneumonitis J12–J18 or J69.0 | 11,175 (33.22%) | 11,229 (4.57%) | 7.27 (7.10–7.44) |
| In-hospital death | 5,003 (14.87%) | 7,746 (3.15%) | 4.72 (4.56–4.88) |
| Pneumonia occurring after 48 hours U69.01 | 5,575 (16.57%) | 4,664 (1.90%) | 8.73 (8.41–9.06) |
| Pneumonia present by 48 hours U69.04 | 5,438 (16.16%) | 6,195 (2.52%) | 6.41 (6.19–6.63) |
| Volume depletion E86 | 4,096 (12.17%) | 10,946 (4.46%) | 2.73 (2.64–2.83) |
| Hypoxemic acute respiratory failure J96.00 | 5,067 (15.06%) | 8,617 (3.51%) | 4.29 (4.15–4.44) |
| Unspecified severe protein-energy malnutrition E43 | 216 (0.64%) | 318 (0.13%) | 4.96 (4.17–5.89) |

All diagnostic endpoints refer to secondary diagnoses. RR, risk ratio; CI, confidence interval. Intervals use an independent-episode model and do not represent uncertainty from coding, confounding, hospital clustering or repeated admissions. J69.0 is not restricted to bacterial pneumonia. U69 codes are defined for fully inpatient adults; the displayed proportions use the full care cohort, which contains 22 episodes aged under 18 years. U69.01 and U69.04 were not assumed to be mutually exclusive. E43 does not cover every form of malnutrition.

The absolute risk difference for J69.0 was 21.38 percentage points (95% CI 20.92–21.83). For the combined J12–J18 or J69.0 endpoint it was 28.64 percentage points.

## Table 3 Mutually exclusive pulmonary coding categories

| Category | R13 secondary diagnosis | No R13 secondary diagnosis |
| --- | ---: | ---: |
| J12–J18 without J69.0 | 3,374 (10.03%) | 6,785 (2.76%) |
| J69.0 without J12–J18 | 7,300 (21.70%) | 4,203 (1.71%) |
| Both J12–J18 and J69.0 | 501 (1.49%) | 241 (0.10%) |
| Neither code group | 22,468 (66.78%) | 234,405 (95.43%) |

The four categories sum to the corresponding full group denominator. This partition counts each hospital episode once and avoids double counting coexisting codes. It is a coding classification, not a clinical adjudication of mutually exclusive mechanisms.

## Table 4 Length of stay contrasts

| Comparison | Dysphagia episodes covered | Mean difference in days with 95% CI | Associated bed-days |
| --- | ---: | ---: | ---: |
| Overall unadjusted | 33,643 (100%) | 8.85 (8.67–9.04) | 297,899 |
| Within DRGs with estimable values in both groups | 33,063 (98.28%), 171 DRGs | 3.61 (3.45–3.78) | 119,423 |
| Within DRGs with at least 20 episodes per group | 32,105 (95.43%), 59 DRGs | 3.60 (3.44–3.76) | 115,553 |

Mean hospital stay was 16.26 days (sample SD 17.14) with an R13 secondary diagnosis and 7.41 days (sample SD 7.15) without one. Within-DRG means are weighted to the observed distribution of episodes with dysphagia. Associated bed-days multiply observed mean differences by exposed-group counts; they are not estimates of preventable bed-days or economic savings. DRG grouping may itself be influenced by dysphagia, complications and treatment.

## Table 5 Exploratory age and survivor analyses

| Analysis | R13 secondary diagnosis | No R13 secondary diagnosis | Contrast with 95% CI |
| --- | ---: | ---: | ---: |
| Mortality, age under 65 | 250/4,756 (5.26%) | 683/62,818 (1.09%) | RR 4.83 (4.20-5.57) |
| Mortality, age 65-79 | 1,284/11,240 (11.42%) | 2,150/90,633 (2.37%) | RR 4.82 (4.51-5.15) |
| Mortality, age 80 or older | 3,469/17,647 (19.66%) | 4,913/92,183 (5.33%) | RR 3.69 (3.54-3.84) |
| Mortality, directly age-standardized | 13.1696%; underlying n = 33,643 | 3.22435%; underlying n = 245,634 | RR 4.08 (3.95-4.23) |
| Stay among episodes ending in discharge alive | n = 28,640; 16.72 days (SD 17.63) | n = 237,888; 7.32 days (SD 6.97) | Difference 9.40 days (9.19-9.60) |
| Restricted survivor within-DRG comparison | n = 27,222; 95.05% of dysphagia survivors | n = 228,798; 58 common DRGs | Difference 3.59 days (3.41-3.78) |

The standardized mortality rates are weighted risks, not observed event counts; the reference is the pooled three-band age distribution of the full OPS cohort. Survivor SDs are sample SDs reconstructed from moments. The restricted survivor DRG comparison uses only exactly reconstructable strata and is weighted to the included dysphagia-survivor distribution. Its comparator count describes available episodes rather than the analysis weights. Confidence intervals are model-based and do not account for clustering or residual confounding. The restricted I63 sensitivity in Table 6 excludes I63.6 explicitly; no result is inferred for the omitted I63.6 death rows. All analyses in this table are exploratory.

## Table 6 Administrative complexity and clinical subgroup sensitivities

| Analysis | R13 secondary diagnosis | No R13 secondary diagnosis | RR with 95% CI |
| --- | ---: | ---: | ---: |
| Mortality standardized by PCCL | 11.47% | 3.59% | 3.20 (3.07-3.33) |
| J12-J18 pneumonia standardized by PCCL | 6.99% | 3.39% | 2.07 (1.97-2.16) |
| Mortality principal I63 excluding I63.6 | 3,871/26,604 (14.55%) | 5,556/149,351 (3.72%) | 3.91 (3.76-4.07) |
| Mortality principal I61 | 611/3,364 (18.16%) | 1,084/8,784 (12.34%) | 1.47 (1.34-1.61) |
| Mortality Barthel Index 0-15 U50.50 | 1,894/9,215 (20.55%) | 2,244/11,843 (18.95%) | 1.08 (1.03-1.15) |
| Mortality extended Barthel Index 0-15 U51.20 | 334/1,093 (30.56%) | 400/1,332 (30.03%) | 1.02 (0.90-1.15) |

PCCL rows are weighted risks standardized to the pooled distribution of all 279,277 episodes across seven PCCL categories; they are separate from age standardization. All other rows are crude comparisons within the explicitly named subgroups. I63 excluding I63.6 contains I63.0, I63.1, I63.2, I63.3, I63.4, I63.5, I63.8 and I63.9. Functional subgroups may overlap and are not a partition of the full cohort. The two severe functional categories summarize the clinically important restriction; all 21 candidate categories, including non-estimable results, appear in Supplementary Tables S1-S2. None of these comparisons provides simultaneous control for all baseline risk factors. All analyses and intervals are exploratory and model-based.

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

## Data and classification sources

- **[InEKData2025]** InEK GmbH. Unterjährige Datenlieferung DRG Januar bis Dezember 2025, data delivery January 16, 2026, classifications 2025. [Data browser](https://datenbrowser.inek.org/DRG202601).
- **[InEKManual2026]** InEK GmbH. InEK DatenBrowser user manual, version September 1, 2026; dataset section 2.51. [Manual](https://datenbrowser.inek.org/assets/manual/InekDatenBrowser.pdf).
- **[BfArMOPS2025]** BfArM. OPS 2025, neurological complex treatment codes 8-981 and 8-98b. [Official classification](https://klassifikationen.bfarm.de/ops/kode-suche/htmlops2025/block-8-97...8-98.htm).
- **[BfArMR132025]** BfArM. ICD-10-GM 2025, R13 dysphagia. [Official classification](https://klassifikationen.bfarm.de/icd-10-gm/kode-suche/htmlgm2025/block-r10-r19.htm).
- **[BfArMU692025]** BfArM. ICD-10-GM 2025, U69 pneumonia-timing codes. [Official classification](https://klassifikationen.bfarm.de/icd-10-gm/kode-suche/htmlgm2025/block-u69-u69.htm).

- **[InEKPCCL2025]** InEK GmbH. Abschlussbericht zur Weiterentwicklung des aG-DRG-Systems fuer das Jahr 2025. December 19, 2024. Section 3.3.1.4, CCL matrix and PCCL. [Official report](https://www.g-drg.de/content/download/14761/file/Abschlussbericht_aG-DRG_2025_2024-12-19.pdf).
- **[BfArMFunction2025]** BfArM. ICD-10-GM 2025, U50-U52 functional impairment codes and assessment timing. [Official classification](https://klassifikationen.bfarm.de/icd-10-gm/kode-suche/htmlgm2025/block-u50-u52.htm).
- **[BfArMBarthel2025]** BfArM. ICD-10-GM 2025, Barthel Index criteria according to the Hamburg Manual. [Official scoring criteria](https://klassifikationen.bfarm.de/icd-10-gm/kode-suche/htmlgm2025/zusatz-06-anh-barthelindex.htm).

Literature and original coding sources accessed November 16, 2026; additional PCCL and functional coding sources verified November 17, 2026. Stable citation keys are retained to support reference-manager conversion before journal submission.

# Supplementary functional analyses

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

The bibliography contains 26 journal publications plus eight official data or coding sources. It includes clinical cohorts, nationwide registries, administrative analyses, randomized trials, a consensus definition and reporting/clinical guidelines. Effect measures retain their original meaning: published adjusted odds ratios and hazard ratios are not directly equated to the current unadjusted risk ratios.

Ungerer 2026 is a direct predecessor using German national DRG data, so the current manuscript makes no first-national-FEES-analysis claim. The main incremental contribution is the 2025 inpatient burden analysis, exact handling of overlapping pulmonary diagnoses, descriptive DRG-stratified hospital-stay comparison, and transparently bounded diagnosis, PCCL and functional sensitivities. Ho 2018 defines dysphagia through nasogastric-tube use and therefore represents a different phenotype. Vasan 2023 supplies a counterexample to uniformly increased inpatient mortality in coding-based studies. Horn 2026 is exploratory and does not validate a severity score for German R13 codes. QASC evaluates a multicomponent bundle; PHAST-TRAC evaluates a selected tracheotomized population. Their results cannot be generalized into an efficacy claim for procedures recorded in these exports.

Before journal submission, the search should be updated and the final wording checked against complete texts of every retained reference. Reference selection here supports contextual interpretation rather than an exhaustive evidence synthesis.

# Author completion note

The statistical results in this draft are based on verified aggregate exports. Before submission, the authors should finalize authorship and affiliations, corresponding-author details, institutional ethics approval or waiver determination, funding and conflicts of interest, contributor roles, the intended journal and any required reporting checklist. Data availability should identify the exact InEK release and applicable access conditions. Analysis code and query definitions are maintained in the private project repository for author review: [https://github.com/benlabeit/inek-dysphagia-acute-2025](https://github.com/benlabeit/inek-dysphagia-acute-2025). Public availability at publication remains to be arranged. A statement on use of generative AI should follow the selected journal's policy and accurately describe the authors' verification and responsibility.

No author list, ethics approval, funding source, conflict declaration or patient-level adjustment has been assumed. Separate age- and PCCL-standardized outcomes, diagnosis-restricted comparisons, functional-category sensitivities and survivor analyses were reconstructed from the verified aggregate exports using the methods above. The companion early-rehabilitation manuscript should be disclosed as a related analysis of the same data source.
