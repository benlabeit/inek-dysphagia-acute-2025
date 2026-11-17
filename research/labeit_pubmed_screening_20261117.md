# Bendix Labeit: complete PubMed author inventory and manuscript relevance screening

Search and screening date: 17 November 2026. Purpose: supplementary author-focused search for the acute cerebrovascular complex-care and early neurological/neurosurgical rehabilitation InEK manuscripts. This is a transparent narrative-search supplement, not a systematic review of all dysphagia literature.

## Search methods and coverage

PubMed was queried through NCBI E-utilities ESearch and all returned records were downloaded in EFetch XML. No language, publication-type, or start-date limits were applied. The retrieval cutoff was 17 November 2026; electronic and issue dates were checked to avoid using later publications. The author query was deliberately broader than a dysphagia-only query so that every retrieved publication could be assessed.

| Exact submitted query | Records | Interpretation |
|---|---:|---|
| `Labeit B[Author]` | 66 | Master inventory |
| `Labeit Bendix[Full Author Name]` | 65 | Full-name crosscheck |
| `Labeit BR[Author]` | 0 | Initials-variant crosscheck |
| `Labeit Bendix Ruven[Full Author Name]` | 0 | Full-name-variant crosscheck |
| `0000-0001-6094-3869[Author Identifier]` | 14 | Identifier crosscheck; PubMed translated this to an All Fields search; no additional records |
| `Labeit[Author] AND (dysphagia[Title/Abstract] OR swallowing[Title/Abstract])` | 63 | Topic/surname crosscheck; no additional records |

The master query was also paginated with `retmax=20` and `retstart=0,20,40,60`. These four pages yielded 66 records and 66 unique PMIDs, exactly matching the unpaginated master set (`retmax=1000`). Thus pagination was not truncated. Full query URLs, PubMed query translations, identifiers, and raw results are retained in the companion JSON files. The ORCID query is an auxiliary check and is not claimed to be an exhaustive identifier search.

Sixty-five records explicitly named Bendix Labeit. One record (PMID 41860704) used the initial-only name B Labeit and was disambiguated using the Düsseldorf neurology affiliation and public institutional email. No conflicting Labeit homonym was identified among the 66 records. This inventory is complete for the stated PubMed query and crosschecks on the retrieval date; it does not claim to capture publications absent from PubMed or records indexed later.

## Screening approach and outcomes

Every record was screened using its title, author list, publication type, available abstract, and relevance to the two manuscript questions. Full text was reviewed selectively when needed for a central interpretation, including the original postextubation pharyngeal electrical stimulation trial. A full-text quality appraisal of all 66 publications was not performed. Records without an abstract were assessed conservatively; letters and the linked erratum were not treated as new outcome studies. No numerical claim was inferred from a title alone.

`include` denotes a directly useful candidate supporting a specific manuscript question or interpretation. `context` denotes adjacent evidence that is indirect, disease-specific, redundant, or unnecessary for the current claims. `exclude` denotes no useful contribution to these manuscripts. `correction` denotes a linked erratum, not independent evidence. These decisions identify eligible supporting sources; they do not require all candidate papers to be cited. The strongest, least redundant source should be preferred for each substantive claim.

| Decision | Acute manuscript | Rehabilitation manuscript |
|---|---:|---:|
| Include candidates | 20 | 21 |
| Context only | 18 | 35 |
| Exclude | 27 | 9 |
| Linked correction | 1 | 1 |
| Total screened | 66 | 66 |

Twenty-eight unique publications were include candidates for at least one manuscript. The companion CSV and JSON give a reason, claim mapping, limitations, PMID, DOI, and verified bibliographic metadata for every record.

## Suggested methods paragraph for either Online Resource

An additional author-focused PubMed search was completed on 17 November 2026 using `Labeit B[Author]`, with full-name, initials-variant, identifier and dysphagia/swallowing crosschecks. The master query returned 66 unique records; explicit pagination in four batches of up to 20 confirmed complete retrieval. All 66 records were individually screened for relevance to both manuscripts using titles, publication types and available abstracts, with selective full-text verification of central claims. Twenty records were potentially relevant to the acute manuscript and 21 to the rehabilitation manuscript (28 unique records across both). Overlapping reports, letters and disease-specific studies were not cited solely because of authorship. The search had no language or publication-type restrictions and was not designed as a systematic review. The complete inventory, query translations and record-level decisions are supplied in the accompanying search files.

## Critical interpretation notes

- Suntrup-Krueger 2023 (PMID 37789340), Suntrup-Krueger 2025 (PMID 40383663), and Labeit 2026 economic analysis (PMID 41803360) are reports from the same 60-patient randomized postextubation PES trial, not three independent trials. Its primary reintubation endpoint was not statistically significant (13% versus 33%, p=0.067). The economic analysis did not establish a significant mean expenditure reduction (one-sided p=0.087) or general cost effectiveness. The 2024 pre-extubation PES study (PMID 38581884) is a different prospective/historical-control study, not another randomized trial.
- The GEMIDAS dysphagia-outcomes and dehydration papers (PMIDs 42361766 and 42862540) share a German geriatric registry source. They provide complementary analyses, not independent replication. Their older inpatient population and use of dysphagia as main or secondary diagnosis differ from the InEK cohorts. Adjusted odds ratios must not be described as risk ratios or causal effects.
- The FEES implementation survey (PMID 41851886) concerns self-reported service access and practices among instructors. It is not a patient-level census of inpatient utilization and does not prove that a particular FEES coding rate represents guideline nonadherence.
- The outpatient reassessment series (PMID 41744255) is a selected referral cohort. Changes in diagnosis or management are not evidence of improved clinical outcomes without a comparator.
- The geriatric cough-force and FEES-feature reports (PMIDs 40606509 and 42304253) appear to use the same 98-person cohort; avoid presenting them as independent replication.
- PMID 37318543 is a linked correction to PMID 37160432. The correction text was not used as independent scientific evidence. The PubMed abstract for PMID 32257098 contains duplicated/truncated results; no uncertain numerical claim from this record is proposed.

## Bibliographic verification

Complete author lists and identifiers come from primary PubMed EFetch XML. Article locators absent from a `Pagination` element were recovered from the XML electronic-location field when it was an unambiguous numeric article number. In particular, Marae 2026 is *Neurological Research and Practice* 8(1):17 (DOI 10.1186/s42466-026-00473-9), and Labeit 2026 PES costs is *Scientific Reports* 16(1):8556 (DOI 10.1038/s41598-026-43591-9). The Lueg dehydration paper was online first without assigned volume/pages in the retrieved record; none were invented. Files preserve the source XML filename for each record.

## Complete 66-record inventory

| PMID | Year | Reference key | Acute | Rehabilitation | Title |
|---|---:|---|---|---|---|
| [43026607](https://pubmed.ncbi.nlm.nih.gov/43026607/) | 2026 | Muhle2026IndividualizedTDCS | exclude | exclude | Frequency-specific cortical swallowing-network responses following neuroengineering-guided individualized multichannel tDCS. |
| [42862540](https://pubmed.ncbi.nlm.nih.gov/42862540/) | 2026 | Lueg2026Dehydration | include | include | In-hospital mortality in co-occurring dehydration and dysphagia: results from the nationwide GEMIDAS Pro registry. |
| [42567925](https://pubmed.ncbi.nlm.nih.gov/42567925/) | 2026 | Muhle2026CorticalSubnetworks | exclude | exclude | Frequency-specific cortical subnetworks support fast human swallowing. |
| [42469330](https://pubmed.ncbi.nlm.nih.gov/42469330/) | 2026 | Muhle2026DEFISS | include | context | Reliability and validity of the DEFISS score for predicting post-extubation dysphagia and dysphagia-related reintubation after stroke. |
| [42361766](https://pubmed.ncbi.nlm.nih.gov/42361766/) | 2026 | Lueg2026GEMIDAS | include | include | Dysphagia as a geriatric syndrome: nationwide outcomes from the GEMIDAS registry. |
| [42304253](https://pubmed.ncbi.nlm.nih.gov/42304253/) | 2026 | Kocar2026FEESPneumonia | context | include | Multifeature endoscopic swallowing patterns associated with pneumonia in hospitalized geriatric patients: a four-year longitudinal cohort study. |
| [42276582](https://pubmed.ncbi.nlm.nih.gov/42276582/) | 2026 | Jung2026CoughStroke | include | context | Cough reflex testing for dysphagia severity and pneumonia risk after acute stroke: a prospective observational study. |
| [42054965](https://pubmed.ncbi.nlm.nih.gov/42054965/) | 2026 | Brux2026FOODDM | context | context | A multidisciplinary Delphi consensus on the formulation of an optimized oral diet for dysphagia and malnutrition (FOOD-DM). |
| [41860704](https://pubmed.ncbi.nlm.nih.gov/41860704/) | 2026 | Jung2026NeurogeriatricReview | context | context | [Oropharyngeal dysphagia as a neurogeriatric syndrome]. |
| [41851886](https://pubmed.ncbi.nlm.nih.gov/41851886/) | 2026 | Marae2026FEESAccess | include | include | Mapping neurogenic dysphagia diagnostics in Germany: accessibility, implementation practices, and barriers to swallowing endoscopy. |
| [41803360](https://pubmed.ncbi.nlm.nih.gov/41803360/) | 2026 | Labeit2026PESCosts | include | include | Pharyngeal electrical stimulation for postextubation dysphagia after stroke: a randomized trial on hospitalization costs from a health insurance perspective. |
| [41744255](https://pubmed.ncbi.nlm.nih.gov/41744255/) | 2026 | Labeit2026Outpatient | context | include | Impact of a Neurogenic Dysphagia Outpatient Clinic on Diagnosis, Treatment, and Nutrition. |
| [41623427](https://pubmed.ncbi.nlm.nih.gov/41623427/) | 2025 | Hofacker2025DBSDysphagia | exclude | context | Effect of deep brain stimulation on dysphagia in Parkinson's disease: mechanisms, evidence, and outlook. |
| [41571515](https://pubmed.ncbi.nlm.nih.gov/41571515/) | 2026 | Cheng2026Metaplasticity | exclude | exclude | Metaplasticity in swallowing system via cross-modal neurostimulation: A randomized crossover trial with magnetoencephalography. |
| [41349566](https://pubmed.ncbi.nlm.nih.gov/41349566/) | 2025 | Labeit2025Neurogeriatric | include | include | Oropharyngeal dysphagia: a narrative review towards an integrated neurogeriatric perspective. |
| [41295988](https://pubmed.ncbi.nlm.nih.gov/41295988/) | 2026 | Labeit2026GERisearch | exclude | exclude | [Challenges and potential of geriatric research in Germany-Insights from the GERisearch survey]. |
| [41032649](https://pubmed.ncbi.nlm.nih.gov/41032649/) | 2026 | Labeit2026ClassificationComment | context | context | Classifying neurogenic dysphagia: neuroanatomical hierarchy versus clinical syndromology. |
| [40708460](https://pubmed.ncbi.nlm.nih.gov/40708460/) | 2025 | Karisik2025LongTermPSD | context | include | Gaps in Guidelines on Long-Term Management Strategies for Post-Stroke Dysphagia. |
| [40642379](https://pubmed.ncbi.nlm.nih.gov/40642379/) | 2025 | Peranovic2025DementiaFEES | exclude | context | Endoscopic characterization of oropharyngeal dysphagia in patients with dementia. |
| [40606509](https://pubmed.ncbi.nlm.nih.gov/40606509/) | 2025 | Stoev2025CoughForce | context | include | Prognostic value of cough force measured by peak expiratory flow in a 4-year longitudinal cohort study of geriatric patients with oropharyngeal dysphagia. |
| [40383663](https://pubmed.ncbi.nlm.nih.gov/40383663/) | 2025 | SuntrupKrueger2025PESRecovery | include | include | Treating postextubation dysphagia after stroke with pharyngeal electrical stimulation -insights from a randomized controlled pilot trial. |
| [40377204](https://pubmed.ncbi.nlm.nih.gov/40377204/) | 2025 | Labeit2025FoslevodopaCase | exclude | exclude | Subcutaneous Foslevodopa as Novel Rescue Therapy for Akinetic Crisis in Parkinson's Disease: A Case Report. |
| [40202551](https://pubmed.ncbi.nlm.nih.gov/40202551/) | 2025 | SuntrupKrueger2025CognitiveReserve | context | context | Cognitive decline limits compensatory resource allocation within the aged swallowing network. |
| [40091074](https://pubmed.ncbi.nlm.nih.gov/40091074/) | 2025 | Dziewas2025Decannulation | context | include | Decannulation ahead: a comprehensive diagnostic and therapeutic framework for tracheotomized neurological patients. |
| [39849098](https://pubmed.ncbi.nlm.nih.gov/39849098/) | 2025 | Doerner2025IFSH | exclude | exclude | Associations of inferior frontal sulcal hyperintensities on brain MRI with cerebral small vessel disease, cognitive function, and depression symptoms. |
| [39030033](https://pubmed.ncbi.nlm.nih.gov/39030033/) | 2024 | Labeit2024DietReply | context | context | Dietary intervention for post-stroke dysphagia - Authors' reply. |
| [38954267](https://pubmed.ncbi.nlm.nih.gov/38954267/) | 2024 | Sasegbon2024EmergingTreatments | context | include | New and Evolving Treatments for Neurologic Dysphagia. |
| [38720388](https://pubmed.ncbi.nlm.nih.gov/38720388/) | 2024 | Dziewas2024IntegratedFEES | include | include | Systematic approach to contextualize findings of flexible endoscopic evaluation of swallowing in neurogenic dysphagia- towards an integrated FEES report. |
| [38627620](https://pubmed.ncbi.nlm.nih.gov/38627620/) | 2024 | Kudelka2024CGA | context | context | Which Comprehensive Geriatric Assessment (CGA) instruments are currently used in Germany: a survey. |
| [38581884](https://pubmed.ncbi.nlm.nih.gov/38581884/) | 2024 | Muhle2024PESPreExtubation | include | context | Pharyngeal Electrical Stimulation prior to extubation - Reduction of extubation failure rate in acute stroke patients? |
| [38508837](https://pubmed.ncbi.nlm.nih.gov/38508837/) | 2024 | Labeit2024Treatment | include | include | Dysphagia after stroke: research advances in treatment interventions. |
| [38135841](https://pubmed.ncbi.nlm.nih.gov/38135841/) | 2024 | Labeit2024DIGESTFEES | exclude | context | Validation of the DIGEST-FEES as a Global Outcome Measure for Pharyngeal Dysphagia in Parkinson's Disease. |
| [37789340](https://pubmed.ncbi.nlm.nih.gov/37789340/) | 2023 | SuntrupKrueger2023PESPilot | include | include | Pharyngeal electrical stimulation for postextubation dysphagia in acute stroke: a randomized controlled pilot trial. |
| [37596008](https://pubmed.ncbi.nlm.nih.gov/37596008/) | 2023 | Labeit2023Assessment | include | include | The assessment of dysphagia after stroke: state of the art and future directions. |
| [37400784](https://pubmed.ncbi.nlm.nih.gov/37400784/) | 2023 | RegnerNelke2023TBCase | exclude | context | Bilateral vocal cord palsy as complication of CNS tuberculosis. |
| [37375566](https://pubmed.ncbi.nlm.nih.gov/37375566/) | 2023 | Calles2023Sarcopenic | context | context | Sarcopenic Dysphagia Revisited: A Cross-Sectional Study in Hospitalized Geriatric Patients. |
| [37318543](https://pubmed.ncbi.nlm.nih.gov/37318543/) | 2023 | Labeit2023DiagnosticsErratum | correction | correction | [Erratum to: Diagnostics and treatment of post-stroke dysphagia]. |
| [37160432](https://pubmed.ncbi.nlm.nih.gov/37160432/) | 2023 | Labeit2023Diagnostics | include | context | [Diagnostics and treatment of post-stroke dysphagia]. |
| [37021194](https://pubmed.ncbi.nlm.nih.gov/37021194/) | 2023 | Labeit2023Costs | include | include | Costs of post-stroke dysphagia during acute hospitalization from a health-insurance perspective. |
| [36793109](https://pubmed.ncbi.nlm.nih.gov/36793109/) | 2023 | Labeit2023Sensory | include | context | Relationship between post-stroke dysphagia and pharyngeal sensory impairment. |
| [36371409](https://pubmed.ncbi.nlm.nih.gov/36371409/) | 2022 | Labeit2022MedicationPD | exclude | context | Dysphagia for medication in Parkinson's disease. |
| [35966778](https://pubmed.ncbi.nlm.nih.gov/35966778/) | 2022 | Labeit2022Presbyphagia | context | context | Clinical determinants and neural correlates of presbyphagia in community-dwelling older adults. |
| [34862828](https://pubmed.ncbi.nlm.nih.gov/34862828/) | 2022 | Labeit2022MyositisAlgorithm | exclude | context | Detecting myositis as a cause of unexplained dysphagia: Proposal for a diagnostic algorithm. |
| [34836134](https://pubmed.ncbi.nlm.nih.gov/34836134/) | 2021 | Muhle2021GastricMotility | context | context | Oropharyngeal Dysphagia and Impaired Motility of the Upper Gastrointestinal Tract-Is There a Clinical Link in Neurocritical Care? |
| [34678269](https://pubmed.ncbi.nlm.nih.gov/34678269/) | 2022 | Labeit2022FEESVFSS | include | include | Comparison of Simultaneous Swallowing Endoscopy and Videofluoroscopy in Neurogenic Dysphagia. |
| [34394727](https://pubmed.ncbi.nlm.nih.gov/34394727/) | 2021 | Warnecke2021Tensilon | exclude | context | Detecting myasthenia gravis as a cause of unclear dysphagia with an endoscopic tensilon test. |
| [33966636](https://pubmed.ncbi.nlm.nih.gov/33966636/) | 2021 | Muhle2021SESETD | context | include | Standardized Endoscopic Swallowing Evaluation for Tracheostomy Decannulation in Critically Ill Neurologic Patients - a prospective evaluation. |
| [33711182](https://pubmed.ncbi.nlm.nih.gov/33711182/) | 2021 | Labeit2021IIM | exclude | context | Predictors, outcome and characteristics of oropharyngeal dysphagia in idiopathic inflammatory myopathy. |
| [33650729](https://pubmed.ncbi.nlm.nih.gov/33650729/) | 2021 | Claus2021EMST | exclude | context | Expiratory Muscle Strength Training for Therapy of Pharyngeal Dysphagia in Parkinson's Disease. |
| [33521647](https://pubmed.ncbi.nlm.nih.gov/33521647/) | 2021 | Dziewas2021COVID | exclude | context | Dysphagia in Patients With Severe Coronavirus Disease 2019-Potential Neurologic Etiologies. |
| [33449304](https://pubmed.ncbi.nlm.nih.gov/33449304/) | 2021 | SuntrupKrueger2021Capsaicinoids | exclude | exclude | Effect of Capsaicinoids on Neurophysiological, Biochemical, and Mechanical Parameters of Swallowing Function. |
| [33338309](https://pubmed.ncbi.nlm.nih.gov/33338309/) | 2021 | Pawlitzki2021NMOSD | exclude | context | Dysphagia in neuromyelitis optica spectrum disorder and myelin oligodendrocyte glycoprotein antibody disease as a surrogate of brain involvement? |
| [33324915](https://pubmed.ncbi.nlm.nih.gov/33324915/) | 2020 | Warnecke2020SESETDReliability | context | include | Inter-rater and test-retest reliability of the "standardized endoscopic swallowing evaluation for tracheostomy decannulation in critically ill neurologic patients". |
| [33318164](https://pubmed.ncbi.nlm.nih.gov/33318164/) | 2021 | Warnecke2021Classification | include | include | Neurogenic Dysphagia: Systematic Review and Proposal of a Classification System. |
| [33230259](https://pubmed.ncbi.nlm.nih.gov/33230259/) | 2020 | Muhle2020DualTaskHealthy | exclude | exclude | Effects of cognitive and motor dual-tasks on oropharyngeal swallowing assessed with FEES in healthy individuals. |
| [33178124](https://pubmed.ncbi.nlm.nih.gov/33178124/) | 2020 | Nelke2020VocalFoldMG | exclude | context | Bilateral Vocal Fold Paralysis in Myasthenia Gravis: A Case Report and Literature Review. |
| [33084118](https://pubmed.ncbi.nlm.nih.gov/33084118/) | 2021 | Labeit2021DualTaskPD | exclude | context | Effect of cognitive and motor dual-task on oropharyngeal swallowing in Parkinson's disease. |
| [33068056](https://pubmed.ncbi.nlm.nih.gov/33068056/) | 2021 | Muhle2021SensoryStimulation | exclude | exclude | Targeting the sensory feedback within the swallowing network-Reversing artificially induced pharyngolaryngeal hypesthesia by central and peripheral stimulation strategies. |
| [32773397](https://pubmed.ncbi.nlm.nih.gov/32773397/) | 2020 | Claus2020PDPredictors | exclude | context | Predictors of Pharyngeal Dysphagia in Patients with Parkinson's Disease. |
| [32650400](https://pubmed.ncbi.nlm.nih.gov/32650400/) | 2020 | Labeit2020MyositisReview | exclude | context | The Impact of Dysphagia in Myositis: A Systematic Review and Meta-Analysis. |
| [32417630](https://pubmed.ncbi.nlm.nih.gov/32417630/) | 2020 | Labeit2020Freezing | exclude | context | Oropharyngeal freezing and its relation to dysphagia - An analogy to freezing of gait. |
| [32257098](https://pubmed.ncbi.nlm.nih.gov/32257098/) | 2020 | Labeit2020LCIG | exclude | context | Effect of Intestinal Levodopa-Carbidopa Infusion on Pharyngeal Dysphagia: Results from a Retrospective Pilot Study in Patients with Parkinson's Disease. |
| [31381234](https://pubmed.ncbi.nlm.nih.gov/31381234/) | 2019 | Labeit2019SensoryTest | context | context | FEES-based assessment of pharyngeal hypesthesia-Proposal and validation of a new test procedure. |
| [31338062](https://pubmed.ncbi.nlm.nih.gov/31338062/) | 2019 | Labeit2019Jo1Case | exclude | context | Dysphagia as Isolated Manifestation of Jo-1 Associated Myositis? |
| [31280655](https://pubmed.ncbi.nlm.nih.gov/31280655/) | 2019 | SuntrupKrueger2019Extubation | include | context | Extubation Readiness in Critically Ill Stroke Patients. |
| [30253410](https://pubmed.ncbi.nlm.nih.gov/30253410/) | 2018 | Labeit2018NIHSS | include | context | Predicting Dysphagia with National Institute of Health Stroke Scale: Distinction between Infra- and Supratentorial Region is Essential. |
