# Member B — Risk scoring (WQI), risk tiers, HotspotAgent

Branch: `feat/b-risk`  ·  Overview: [team_split.md](../team_split.md)  ·  Rules: `CLAUDE.md`

You turn water chemistry into a risk tier. Everything the system says to a user traces back to your
number, so the framing discipline matters as much as the arithmetic: **this is a risk indicator from
published water-quality research. It is not a CKDu diagnosis and not a causal claim.**

---

## 1. Files you own

| File | What it does |
|---|---|
| `src/core/wqi.py` | Water Quality Index per well. Pure — no SPADE imports. |
| `src/core/risk_tiers.py` | WQI → risk tier per well, and well tiers → village tier. |
| `src/agents/risk_scoring.py` | RiskScoringAgent — WQI per well, risk tier per village, per month. |
| `src/agents/hotspot.py` | HotspotAgent — compares village risk with published CKDu aggregates. |
| `tests/test_wqi.py`, `tests/test_risk_tiers.py` | Your tests. |

## 2. The method, exactly as published

From `data/raw/ckdu_02_wqi_method_and_thresholds.csv` (Cooray et al. 2019, IJERPH 16:1698, Sec 2.3):

```
WQI = Σ (Wi · qi)
qi  = (Ci / Si) · 100
Wi  = wi / Σ wi
```

- `Ci` = measured concentration (mg/L)
- `Si` = Sri Lankan drinking water standard for that parameter
- A sample exactly meeting the standard scores **90** — use that as your first sanity test.

**Classes** (Table 2): Excellent `<50` · Good `50–100` · Poor `100–200`.
Their samples never exceeded 200, so no higher class was defined. If you need one, take it from
Table S2 — **do not invent a class**.

**Confirmed weights:** TDS, F, NO3, DOC = `5` (the maximum).

## 3. Two blockers — close these in week 1, before writing the formula

### Blocker 1 — the `TO_FILL` weights

`ckdu_02` row `Weight wi: pH; hardness; alkalinity; Ca; Mg; Na; Cl; SO4; Fe` is `TO_FILL`, and the
`Si` standard values are in the same supplement.

- [ ] Download <https://www.mdpi.com/1660-4601/16/10/1698/s1> — Table S1 (weights) and Table S2
      (SLS values, and any class above 200). The article is CC BY, so reuse with citation is fine.
- [ ] Fill the row in `ckdu_02`, one row per parameter, with `source` naming Table S1.

**Project rule: never invent a threshold or a weight. If the supplement does not give it, stop and
ask the team.** An invented weight silently corrupts every downstream number — C's bids, D's alerts,
the whole evaluation.

### Blocker 2 — the parameter coverage gap

The published WQI uses **13** parameters: pH, TDS, hardness, alkalinity, Ca, Mg, Na, F, Cl, SO4, NO3,
Fe, DOC. But `ckdu_01` — and therefore the 440 synthetic wells — carry only **9**: pH, EC, alkalinity,
hardness, F, DOC, Cl, SO4, Fe.

**Missing: TDS, Ca, Mg, Na, NO3.** Two honest options:

| Option | What it means |
|---|---|
| **(a) Complete the parameters** | Derive TDS from EC (state the conversion factor you use and its source); transcribe Ca, Mg, Na, NO3 from the supplement or from Nikagolla et al. 2020 (27 wells, Tables 1–3, CC BY-NC-ND — transcribe for coursework and cite). Then A regenerates the synthetic wells with the extra parameters. |
| **(b) Reduced-parameter WQI** | Compute over the 9 available parameters, renormalise `Wi` across just those. Then **stop calling it "the Cooray WQI"** — name it a reduced-parameter WQI, say which 5 parameters are absent, and state that the absolute values are not comparable with the paper's. |

- [ ] Decide **with the whole team**, not alone — it changes A's generator, C's bids and D's alerts.
- [ ] Write the decision and its justification into `docs/wqi_method.md` (you create that file).

## 4. Tasks

### Week 3–4 — the WQI

- [ ] `wqi.py`: load weights and `Si` values **from `ckdu_02`**, never hard-coded in Python. If a
      value is `TO_FILL`, raise an error — do not fall back to a default.
- [ ] Sanity test: a synthetic sample sitting exactly on every SLS limit must score ≈ 90.
- [ ] Return the component `qi` values alongside the total, so D's dashboard can show *which*
      parameter drove a village's score. A tier with no explanation is useless to a health officer.
- [ ] Handle a missing parameter explicitly: renormalise and record which parameters were used.
      Never treat missing as zero.

### Week 5–6 — tiers and the agent

- [ ] `risk_tiers.py`: WQI → tier from the published ranges only. Then **well tiers → one village
      tier** — decide the rule (worst well? share of wells above Poor?) and document why. A single
      bad well in a village of twenty is a different situation from all twenty being bad.
- [ ] `RiskScoringAgent`: on each month tick, consume A's readings frame, emit a risk record per
      village. Timeout on every `receive()`. Log every message through D's `msg_log`.

### Week 7–8 — HotspotAgent

- [ ] Compare your village tiers against `ckdu_04_ckdu_aggregate_stats.csv` (district-level CKD/CKDu
      incidence and prevalence, Ranasinghe et al. 2019) and the `ckdu_prevalence_class` column that
      Cooray et al. already assigned to each DS division.
- [ ] Clustering or correlation — k-means / hierarchical on the parameter vectors, or Spearman of
      risk score against prevalence class. Fixed random seed.
- [ ] Report it as an **alignment check, not a validation of causation**. Only 11 divisions and
      district-level aggregates: say so. Do not compute a p-value and present it as proof.

### Week 10 — validate against the literature

`ckdu_05_validation_benchmarks.csv` gives you targets:

- [ ] Cooray et al.: **3.8% wet / 2.6% dry excellent**, **28.2% wet / 30.3% dry poor**. Run your tiers
      over the synthetic wells. Land nowhere near that distribution and either your WQI or A's
      generator is wrong — find out which before week 11.
- [ ] Chandrajith et al. 2023: >88% of CKDu patients' wells showed excess hardness, 44% had F > 0.60 mg/L.
- [ ] Nikagolla et al. 2020: >60% of shallow wells had F > 0.6 mg/L, and **the authors state the data
      are insufficient to prove a chemistry–CKDu link**. Quote that in your report section.

## 5. Interfaces

```python
# you consume, from A
readings_frame  # well_id, ds_division, month, season, source + 9 parameters

# you publish, consumed by C (bids) and D (alerts, dashboard)
risk_record = {
    "ds_division": str,
    "month": int,
    "wqi": float,            # village aggregate
    "tier": str,             # "Excellent" | "Good" | "Poor"
    "drivers": {str: float}, # top contributing qi components
    "n_wells": int,
    "source": str,           # "real" | "synthetic" | "mixed"
}
```

## 6. Wording you must not drift from

- "Risk indicator derived from published water-quality thresholds." ✅
- "This well is unsafe / causes CKDu / indicates CKDu." ❌
- Carry the uncertainty into docstrings, not just the report — the next person reading `wqi.py`
  should see it.

## 7. Before you say a task is done

```
pytest -q
```
Show the command and its output. For the WQI, also show the ≈ 90 sanity check passing and your tier
distribution next to Cooray et al.'s published percentages.

## 8. Prompts that work in Claude Code

- `Read CLAUDE.md and docs/tasks/member_b_risk_and_hotspot.md. Implement src/core/wqi.py reading weights and Si values from data/raw/ckdu_02_wqi_method_and_thresholds.csv. Raise on TO_FILL. Add pytest tests including the score-90 sanity check.`
- `Compute my tier distribution over data/processed/synthetic_wells.csv and compare it with the Cooray percentages in ckdu_05. Show the numbers.`
