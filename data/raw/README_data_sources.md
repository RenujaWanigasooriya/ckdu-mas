# CKDu well-water MAS: data pack

Everything here comes from published papers or is clearly labelled synthetic. Nothing is a live feed.

## Files

| File | What it is | Real or synthetic |
|---|---|---|
| `ckdu_01_water_quality_area_stats.csv` | Min/Max/Avg of pH, EC, alkalinity, hardness, F, DOC, Cl, SO4, Fe by CKDu prevalence class (High, Moderate, Mild, Non-prevalence, All) and season | Real (Cooray et al. 2019, Table 1) |
| `ckdu_02_wqi_method_and_thresholds.csv` | WQI formula, class ranges, and the standards/thresholds the papers state | Real; some weights still `TO_FILL` |
| `ckdu_03_sampling_design_ds_divisions.csv` | The 11 DS divisions/districts sampled and the samples per season | Real counts; population, depot distance, coordinates left blank for you |
| `ckdu_04_ckdu_aggregate_stats.csv` | District-level CKD/CKDu incidence, prevalence ranges, survival and counts | Real (Ranasinghe et al. 2019) |
| `ckdu_05_validation_benchmarks.csv` | Published findings you can compare your risk tiers against | Real |
| `generate_synthetic_wells.py` | Creates individual wells calibrated to file 01 | Script |
| `synthetic_wells.csv` | 440 generated readings (20 wells x 11 divisions x 2 seasons), `source` column = `synthetic` | **Synthetic** |

## What I could not get (and how you can)

1. **Sample-level well data from Cooray et al. 2019** (Supplementary Table S3) and the **remaining WQI weights and SLS values** (Table S1, S2). The supplement is a binary file I could not read here. Download it from https://www.mdpi.com/1660-4601/16/10/1698/s1 and fill the `TO_FILL` row in file 02. The article is CC BY, so you can reuse it with citation.
2. **DS-level incidence and prevalence** (Table 2 of Ranasinghe et al. 2019). The site blocks automated access. Open https://link.springer.com/article/10.1186/s12882-019-1501-0 and transcribe the table (CC BY). The ten GPS-mapped DS divisions are: Madawachchiya, Kabethigollawa, Padaviya, Rambewa, Horowpathana, Kahatagasdigiliya (Anuradhapura); Madirigiriya, Dimbulagala, Hingurakgoda, Elahara (Polonnaruwa).
3. **Sample-level data from Nikagolla et al. 2020** (27 wells: Tables 1-3, including trace elements and isotopes). That manuscript is licensed CC BY-NC-ND, so I did not copy its tables. Transcribe them yourselves for coursework and cite the paper: https://eprints.qut.edu.au/210507
4. **Large national groundwater dataset.** Shamsudduha et al. 2025 (Scientific Reports 15:10187) collated 1,252 groundwater records from NWSDB and the Water Resources Board. The data are not public, but the authors say processed datasets can be provided for research on request. Email the authors citing your MSc coursework.
5. **Official CKDu registry data.** Ranasinghe et al. say aggregated data come from the Renal Disease Prevention and Research Unit, Ministry of Health, on reasonable request with permission of the Director General of Health Services; some aggregates are on the renal registry site (https://nicst.com/iframe-renal-dev/).

## Caveats to state in your report

- Incidence values in file 04 have no unit in the text I could read. Check Figure 1 of the paper before quoting a unit.
- Ranasinghe et al. give point prevalence of 1.52-3.35 (Anuradhapura) and 0.67-1.25 (Polonnaruwa) in the Results but 2.44-4.35 in the Abstract. Cite the Results figures and note the inconsistency.
- Cooray et al. sampled 88 locations across 11 areas (35 High, 26 Moderate, 17 Mild, 10 controls) and collected two sets per location; their abstract says 88 samples. Check the paper's Methods before reporting your sample size.
- Several papers conclude that the water chemistry-CKDu link is not proven (Nikagolla et al. 2020 say so directly). Keep your system framed as a risk-indicator tool.
- Synthetic wells use an assumed correlation (RHO = 0.6) between parameters. That is not a published value. Disclose it.

## Sources

- Cooray T, et al. (2019). Assessment of Groundwater Quality in CKDu Affected Areas of Sri Lanka. Int J Environ Res Public Health 16(10):1698. doi:10.3390/ijerph16101698 (CC BY)
- Ranasinghe AV, et al. (2019). Incidence, prevalence and trends of CKD and CKDu in the North Central Province of Sri Lanka: an analysis of 30,566 patients. BMC Nephrol 20:338. doi:10.1186/s12882-019-1501-0 (CC BY 4.0)
- Nikagolla C, et al. (2020). Using water quality and isotope studies to inform research in CKDu endemic areas in Sri Lanka. Sci Total Environ 745:140896. doi:10.1016/j.scitotenv.2020.140896
- Shamsudduha M, et al. (2025). Assessing the water quality hazard and challenges to achieving the freshwater goal in Sri Lanka. Sci Rep 15:10187. doi:10.1038/s41598-025-93845-1
- Kafle K, Balasubramanya S, Horbulyk T (2019). Prevalence of chronic kidney disease in Sri Lanka: a profile of affected districts reliant on groundwater. Sci Total Environ 694:133767. doi:10.1016/j.scitotenv.2019.133767
- Horbulyk T, Kafle K, Balasubramanya S (2021). Community response to the provision of alternative water supplies. Water International 46(1):37-58. doi:10.1080/02508060.2020.1868124
- Chandrajith R, et al. (2023). Geochemical characteristics of groundwater consumed by patients with CKDu in the crystalline dry zone terrain of Sri Lanka. Exposure and Health.
- Balasooriya S, et al. (2020). Possible links between groundwater geochemistry and CKDu: Ginnoruwa region. Exposure and Health 12(4):823-834.
