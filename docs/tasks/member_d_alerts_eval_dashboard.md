# Member D — AlertAgent, infrastructure, evaluation, dashboard, report

Branch: `feat/d-integration`  ·  Overview: [team_split.md](../team_split.md)  ·  Rules: `CLAUDE.md`

You own the two things every other member depends on — the **message schema** and the **message
log** — plus everything a marker actually looks at: the alerts, the metrics, the dashboard and the
report. Your week 1 is on the critical path for all four people, so do it first and do it carefully.

---

## 1. Files you own

| File | What it does |
|---|---|
| `src/core/ontology.py` | **The shared contract.** JSON schema + performatives for every message type. |
| `src/core/msg_log.py` | Appends every message to `logs/messages.csv`. |
| `src/agents/alert.py` | AlertAgent — tiered, non-alarmist alerts. |
| `src/sim/evaluate.py` | The four graded metrics, computed from the logs. |
| `dashboard/app.py` | Streamlit + Folium. Reads log files; does **not** run inside the agent process. |
| `tests/test_ontology.py`, `tests/test_evaluate.py` | Your tests. |

## 2. Week 1 — the shared foundation (blocking for A, B and C)

### `src/core/ontology.py`

- [ ] One documented schema per message type. Every body is JSON. Document the schema **in this
      file** — `CLAUDE.md` names it as the single source of truth.
- [ ] Performatives, all six: `cfp`, `propose`, `refuse`, `accept-proposal`, `reject-proposal`,
      `inform`, plus `failure`.
- [ ] Message types to cover: month tick (Clock → all), well readings (WellMonitor → RiskScoring),
      risk record (RiskScoring → Coordinator, Alert, Hotspot), the five Contract Net messages,
      and the alert itself (Alert → village health officer).
- [ ] A validator: `validate(performative, body)` raising on a missing or unexpected field. Run it in
      every agent before sending — it catches the integration bugs that otherwise surface in week 9.
- [ ] Get all four to review it, then **freeze it at end of week 3**. After the freeze, a change needs
      everyone's agreement because it breaks four agents at once.

### `src/core/msg_log.py`

- [ ] Append-only CSV at `logs/messages.csv`, columns exactly:
      `timestamp, sender, receiver, performative, thread_id, payload`
- [ ] `payload` as a JSON string in one column — keeps the CSV readable and lets you reconstruct a
      full negotiation thread later.
- [ ] Safe for concurrent writes: several SPADE agents in separate processes write to it at once.
      Lock, or one line per write with a flush. Verify with the toy demo, do not assume.
- [ ] Also log *received* messages, not only sent ones. Alert latency needs both ends.

## 3. Tasks

### Week 3–4 — alert wording (draft early, review with all four)

This is the main place the project can lose marks on framing. Write the exact strings and get the
whole team to sign off.

| Tier | Message intent | Example wording |
|---|---|---|
| Good | Informational, no action | "This month's water-quality indicators for your well are within published guideline ranges." |
| Poor | Advise an alternate source | "Water-quality indicators for this well are outside published guideline ranges for drinking water. Where possible, use an alternate source (RO-treated or piped supply) for drinking and cooking." |
| Poor + hotspot | Advise alternate source and routine screening | "…and routine kidney-health screening is available at your nearest clinic." |

Rules for every string:

- ✅ "Risk indicator derived from published water-quality thresholds."
- ❌ Never "unsafe", "contaminated", "causes CKDu", "you may have CKDu", or any diagnosis.
- ❌ Never state that water chemistry causes CKDu. Several of the cited papers — Nikagolla et al.
  2020 explicitly — conclude the link is **not proven**.
- Non-alarmist tone. The real-world failure mode of a system like this is panic, not under-reaction.

### Week 5–6 — AlertAgent

- [ ] Consume B's risk records and HotspotAgent output; emit a tiered alert per village per month.
- [ ] Suppress repeats: do not re-alert an unchanged tier every single month. Alert on **tier change**
      or on a documented re-reminder interval. Log the suppression decision so latency stays measurable.
- [ ] Timeout on every `receive()`.

### Week 7–8 — `src/sim/evaluate.py`

Four metrics, all computed from `logs/messages.csv` and `logs/allocations.csv`:

- [ ] **Risk-classification alignment** — your village tiers vs the documented case-density patterns
      in `ckdu_04` and the `ckdu_prevalence_class` column in `ckdu_03`. Report it as an alignment
      check; **not** a validation of causation.
- [ ] **Allocation efficiency** — Contract Net vs equal-split vs first-come, on the shared metric
      (risk-weighted population served). Agree the exact definition with C.
- [ ] **Alert latency** — timestamp of the reading entering the system → timestamp of the alert.
      Needs both sent and received messages in the log.
- [ ] **Negotiation efficiency** — Contract Net rounds and message count per month.
- [ ] Output one `logs/evaluation_summary.csv` plus a printed table, so the result is quotable in the
      report without rerunning anything.

### Week 11 — dashboard

- [ ] `dashboard/app.py`, Streamlit + Folium. Villages coloured by risk tier, using A's `lat`/`lon`.
- [ ] Reads `logs/` only. **It must not run inside the agent process** — start it separately.
- [ ] A month slider, the per-village `drivers` from B's risk records (which parameter drove the
      score), and the allocation outcome per month.
- [ ] **A standing disclaimer on screen:** risk indicators from published water-quality research;
      not a CKDu diagnosis; synthetic data clearly labelled.
- [ ] Mark real vs synthetic visibly — a marker should never have to guess which is which.

### Weeks 9 and 12 — integration and demo

- [ ] Week 9: all seven agent types running together in one `src/sim/runner.py` invocation. You are
      the integration lead — chase the interface mismatches.
- [ ] Week 12: rehearse the demo. **Everyone explains a part they do not own.**

## 4. Report — the limitations section is yours

Carry all of these in, from `data/raw/README_data_sources.md`:

- Real datasets are **small** — tens to ~90 samples per study. Do not overstate generalizability.
- Synthetic data is disclosed: 440 rows, all `source=synthetic`, with `RHO = 0.6` an **unpublished
  assumption** (A documents it in `docs/data_assumptions.md`).
- `ckdu_04` incidence values have **no unit** in the text we could read — check Figure 1 of
  Ranasinghe et al. before quoting a unit.
- Ranasinghe et al. give point prevalence **1.52–3.35** (Anuradhapura) and **0.67–1.25**
  (Polonnaruwa) in the Results but **2.44–4.35** in the Abstract. Cite the Results figures and note
  the inconsistency.
- Cooray et al. sampled 88 locations across 11 areas and collected two sets per location; the
  abstract says 88 samples. Check their Methods before stating your own sample size.
- Several papers conclude the chemistry–CKDu link is **not proven**. Say so plainly — it is a
  strength of the report, not a weakness.
- If B took the reduced-parameter WQI route (5 of 13 parameters unavailable), that limitation is
  reported here too.

## 5. Interfaces you publish

```python
# every agent imports these
from src.core.ontology import validate, PERFORMATIVES, SCHEMAS
from src.core.msg_log import log_message

log_message(sender, receiver, performative, thread_id, payload)
# -> logs/messages.csv: timestamp, sender, receiver, performative, thread_id, payload
```

## 6. Before you say a task is done

```
pytest -q
spade run                              # terminal 1
python -m src.sim.demo_contract_net    # terminal 2
python -m src.sim.evaluate
streamlit run dashboard/app.py
```
Show each command and its output — `messages.csv` rows, the evaluation table, a dashboard
screenshot. Not a claim that it works.

## 7. Prompts that work in Claude Code

- `Read CLAUDE.md and docs/tasks/member_d_alerts_eval_dashboard.md. Implement src/core/ontology.py and src/core/msg_log.py with pytest tests. Cover all seven performatives and a validate() that raises on missing fields.`
- `Write the AlertAgent tier strings from section 3 of my task doc. Check every string against the framing rules in CLAUDE.md — no diagnosis, no causal claim.`
- `Implement src/sim/evaluate.py computing all four metrics from logs/messages.csv and logs/allocations.csv. Show me the output table.`
