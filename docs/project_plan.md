# Multi-Agent System for a CKDu Well-Water Safety Network

**Course:** Multi-Agent Systems — MSc in Data Science and Artificial Intelligence
**Institution:** University of Sri Jayewardenepura
**Team size:** 4

---

## 1. Problem Statement

Chronic Kidney Disease of unknown etiology (CKDu) has affected tens of thousands of farmers in Sri Lanka, concentrated in the North Central Province (Anuradhapura and Polonnaruwa districts), with a documented spread into other regions including the Northern Province. The exact cause remains scientifically debated — it is generally described as multi-factorial (CKDu-mfo) — but a strong and consistently reported association exists between CKDu prevalence and groundwater quality: water hardness, fluoride, salinity, dissolved organic carbon (DOC), and trace elements such as cadmium and arsenic in shallow wells used for drinking water.

Currently, well-water testing and CKDu case surveillance exist as disconnected academic studies and isolated Ministry of Health programs. There is no system that continuously monitors well safety, flags at-risk sources, correlates them with disease patterns, and coordinates a response (alternative water supply, alerts, screening referrals). This is a genuine coordination gap that a multi-agent system is well suited to address.

> **Framing note:** This system must be described and built as a *risk-flagging support tool based on published water-quality indicators*, not a diagnostic system. CKDu causation is still scientifically contested. Avoid any claim that the system "detects" or "diagnoses" CKDu — frame outputs as risk indicators derived from established research thresholds.

## 2. Objectives

1. Continuously score wells for CKDu-associated risk using established water-quality parameters and thresholds from the literature.
2. Correlate well-level risk scores with known disease-cluster patterns to prioritize which areas need attention first.
3. Coordinate scarce safe-water resources (RO units, water bowsers) to the highest-risk villages using a negotiation protocol rather than a static allocation rule.
4. Alert village health officers and affected families early, with appropriately cautious, non-alarmist guidance.

## 3. Multi-Agent Architecture

### 3.1 System flow

```
Well test & health data (water chemistry + CKDu clinic reports)
        |
        v
Well monitoring agent  ->  aggregates water quality readings
        |
        v
Risk scoring agent  ->  computes a Water Quality Index (WQI) per well
        |
        v
Hotspot correlation agent  ->  links well risk to CKDu case clusters
        |
        +---------------------------+
        |                           |
        v                           v
Resource coordination agent   Alert & awareness agent
(negotiates bowsers/RO units) (notifies families & officials)
        |                           |
        +-------------+-------------+
                       v
        Villagers & health authorities
        (safer water, earlier screening)
```

### 3.2 Agent descriptions

| Agent | Role | Key behavior |
|---|---|---|
| **Well monitoring agent** | Data ingestion | Aggregates periodic water-chemistry readings per well (fluoride, hardness, salinity, DOC, cadmium, arsenic, etc.) |
| **Risk scoring agent** | Risk modeling | Computes a Water Quality Index (WQI) per well using threshold-based scoring from CKDu research literature |
| **Hotspot correlation agent** | Pattern detection | Links well risk scores to known CKDu case-density patterns by district/division, using clustering or correlation methods similar to those used in published CKDu studies |
| **Resource coordination agent** | Negotiation | Runs a **Contract Net Protocol** across village agents to allocate a limited pool of RO units/water bowsers when multiple high-risk wells compete for scarce resources |
| **Alert & awareness agent** | Communication | Notifies village health officers and families when a well crosses a risk threshold, with guidance to use an alternate source and seek screening — never a diagnosis |

### 3.3 Why this is a genuine multi-agent problem

- **Autonomy**: each agent (especially per-village monitoring/allocation agents) makes decisions from a local view of its own data.
- **Distributed decision-making**: no single agent has the full picture; risk scores, correlations, and resource requests are computed independently and combined through message passing.
- **Coordination under scarcity**: the resource coordination agent's Contract Net Protocol is the core MAS demonstration — multiple villages competing for a limited pool of RO units/bowsers is a textbook negotiation problem, not just an optimization one.

## 4. Data Sources

### 4.1 Real data sources (verified)

| Source | What it contains | Access notes |
|---|---|---|
| Assessment of Groundwater Quality in CKDu Affected Areas of Sri Lanka (PMC6572134) | 88 groundwater samples, dry (Dec 2016) and wet (May 2017) seasons, dry-zone CKDu areas; includes a Water Quality Index methodology | Open access — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6572134/ |
| Water quality and CKDu in North Central Province (Springer, Applied Water Science, s13201-018-0792-9) | Well-water samples from CKDu patients and non-patients in Anuradhapura and Polonnaruwa; chloride, fluoride, nitrate, phosphate, calcium, magnesium, sodium, cadmium, arsenic | https://link.springer.com/article/10.1007/s13201-018-0792-9 |
| Impact of water quality on CKDu in Thunukkai Division, Mullaitivu (PMC7687782) | Extends the picture to the Northern Province | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7687782/ |
| Incidence, prevalence and trends of CKD/CKDu in NCP: 30,566 patients (BMC Nephrology) | District-level aggregate case data from hospital registers, 2003–2016 | https://bmcnephrol.biomedcentral.com/counter/pdf/10.1186/s12882-019-1501-0.pdf |
| National Research Programme for CKDu in Sri Lanka (Ministry of Health / WHO, 2009, via NSF Sri Lanka Digital Library) | Foundational technical report defining CKDu study groups and geographic distribution | https://dl.nsf.gov.lk/items/9fded6c7-bd67-4942-bda9-e5b56fc71b93/full |
| An integrated data-driven approach for CKDu risk profiling and prediction (SLIIT undergraduate research repository) | A Sri Lankan student project combining GIS, water quality, and health records for CKDu risk prediction | https://rda.sliit.lk/handle/123456789/4913 |

### 4.2 Data sourcing strategy

1. **Pull real well-chemistry data from the open-access studies above.** These are the best source of genuine numbers, even though sample sizes are small (dozens to ~90 samples).
2. **Extract the data tables from the PDFs.** Manually transcribe (feasible given small sample sizes) or use a tool like `tabula-py`/`camelot` for larger tables.
3. **Email your own university's CKDu researchers.** University of Sri Jayewardenepura has had faculty (e.g. Dr. K. Wanigasuriya) actively publishing CKDu research. A short email explaining the coursework project is a realistic route to guidance, anonymized data, or pointers to unpublished datasets.
4. **Use aggregate case statistics, not patient records.** Individual CKDu patient data is medical data and won't be (and shouldn't be) shared without ethics clearance. Use published aggregate statistics — prevalence percentages by district/year, hospital case counts over time.
5. **Get village/well spatial structure from open map data.** Use GADM administrative boundaries or OpenStreetMap for Anuradhapura/Polonnaruwa DS divisions rather than needing precise real well GPS coordinates.
6. **Fill remaining gaps with literature-calibrated synthetic data.** Once you have real means, ranges, and safety thresholds per parameter from the papers, generate additional synthetic well samples using those distributions. Disclose this explicitly in your methodology — undisclosed synthetic data is penalized far more heavily than disclosed synthetic data.

### 4.3 Known limitations

- Official Sri Lankan open data portals (data.gov.lk, data.health.gov.lk) are unlikely to have granular CKDu-specific data; the government has been publicly criticized for not systematically collecting this data.
- Real datasets are small (tens to ~90 samples per study) — be upfront about this in your evaluation section rather than overstating generalizability.
- No live sensor network exists; well readings should be modeled as periodic manual test data (realistic cadence, e.g. monthly), not real-time streaming.

## 5. Technology Stack

- **Agent framework**: SPADE (Python, XMPP-based, FIPA ACL-style messaging) for agent communication and the Contract Net Protocol negotiation in the resource coordination agent.
- **Risk model**: a weighted Water Quality Index formula from the literature, with parameter thresholds hard-coded from the papers above; optionally a clustering or logistic model for the hotspot correlation agent.
- **Data handling**: `pandas` for structuring extracted datasets.
- **Dashboard**: Streamlit + Folium map, color-coding villages/wells by risk tier.

## 6. Evaluation Metrics

| Metric | What it measures |
|---|---|
| Risk-classification alignment | How well predicted risk tiers align with documented case-density patterns from the literature (not a causal claim — a sanity check on the model) |
| Resource allocation efficiency | Negotiated allocation of limited RO units/bowsers vs. a naive equal-split baseline |
| Alert latency | Time from an unsafe reading entering the system to an alert being issued |
| Negotiation efficiency | Number of Contract Net Protocol rounds needed to converge on an allocation |

## 7. Team Roles (4-person split)

1. **Data & monitoring agent lead** — source and structure the water-quality datasets; build the well monitoring agent.
2. **Risk scoring agent lead** — implement the Water Quality Index / risk model from the literature.
3. **Hotspot correlation & resource coordination lead** — clustering/correlation logic plus the Contract Net Protocol negotiation for RO/bowser allocation.
4. **Alert agent, dashboard, integration & evaluation lead** — SPADE messaging integration, dashboard, evaluation metrics, report and demo coordination.

*Note: everyone should still touch the core agent code, since MAS courses often grade individual contribution — this split defines primary ownership, not exclusive responsibility.*

## 8. Timeline (10–12 weeks)

| Week(s) | Milestone |
|---|---|
| 1–2 | Literature review of CKDu water-quality studies; finalize risk thresholds; submit proposal |
| 3–4 | Structure well/village dataset; define agent message ontology |
| 5–6 | Build well monitoring agent + risk scoring agent |
| 7–8 | Build hotspot correlation agent + resource coordination negotiation logic; begin integration |
| 9 | Full system integration and testing |
| 10 | Evaluation against literature-based case patterns |
| 11 | Build dashboard; write final report |
| 12 | Rehearse and deliver demo/presentation |

## 9. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Overclaiming medical certainty | Explicitly frame all outputs as "risk indicators from published water-quality research," not diagnoses — state this in the report and the UI text |
| No live data feed | Use published datasets as realistic seed data; simulate periodic new readings for the demo |
| Small dataset size (tens to ~90 records per study) | Be upfront about this limitation in the evaluation section rather than overstating generalizability |
| Undisclosed synthetic data | Clearly label any literature-calibrated synthetic data as such in the methodology section |

## 10. Suggested Next Steps

- Sketch the exact Water Quality Index formula and safety thresholds from the referenced papers to give the risk scoring agent concrete starting numbers.
- Draft the Contract Net Protocol message sequence (Call-for-Proposals → Propose → Accept/Reject) for the resource coordination agent.
- Reach out to relevant University of Sri Jayewardenepura faculty for guidance before the literature review phase concludes.

---

*Generated as a project planning reference for the Multi-Agent Systems coursework, MSc Data Science and AI, University of Sri Jayewardenepura.*
