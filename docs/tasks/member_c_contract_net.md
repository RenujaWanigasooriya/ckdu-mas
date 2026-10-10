# Member C — Contract Net negotiation, ResourceCoordinatorAgent, baselines

Branch: `feat/c-contractnet`  ·  Overview: [team_split.md](../team_split.md)  ·  Rules: `CLAUDE.md`

You own the core MAS demonstration. A Multi-Agent Systems course grades the negotiation protocol
harder than anything else in this project: a correct FIPA Contract Net over a **genuinely scarce**
resource pool, with logged messages and a measurable advantage over naive baselines.

---

## 1. Files you own

| File | What it does |
|---|---|
| `src/core/allocation.py` | Pure allocation logic + the two baselines. No SPADE imports. |
| `src/agents/resource_coordinator.py` | ResourceCoordinatorAgent — runs the Contract Net. |
| `src/agents/clock.py` | ClockAgent — broadcasts the simulated "new month" tick. |
| `src/sim/runner.py` | Simulation runner — wires ticks to monthly negotiation rounds. |
| `src/sim/demo_contract_net.py` | Week-1 toy demo: 1 coordinator + 3 villages. |
| `src/sim/config.py` | Resource pool sizes, seeds, timeouts. |
| `tests/test_allocation.py` | Your tests. |

## 2. The protocol — all six performatives, no shortcuts

```
Coordinator                               VillageAgents (11)
     |                                              |
     |------------------ cfp ---------------------->|   broadcast: resource, round, deadline
     |<----------- propose / refuse ----------------|   bid, or refuse if no need this month
     |                                              |
     |--- accept-proposal (winners) --------------->|
     |--- reject-proposal (losers) ---------------->|
     |<----------- inform / failure ----------------|   village confirms it can take the resource
```

- `refuse` is not optional. A village with no need that month must refuse, and that must show up in
  the log — it is evidence the agents are autonomous rather than always bidding.
- `failure` is not optional either. Model at least one case where an accepted village cannot take
  delivery, and re-offer to the next-best bidder. That is what makes it a negotiation and not a
  ranked list.
- Multi-round: if the pool is not exhausted and villages remain unserved, issue another CFP. Count
  the rounds — **negotiation rounds to converge is one of the four graded metrics.**

## 3. Scarcity — get this right or there is nothing to evaluate

The pool **must** be genuinely scarce: fewer resources than villages that need them. With 11
villages, something like 3 RO units and 4 bowser trips per month. If every village can be served,
the Contract Net is theatre and your evaluation section has nothing to show.

**Realism anchor** from `data/raw/ckdu_05_validation_benchmarks.csv` — Horbulyk et al. 2021,
survey of ~1500 households: by 2018 only **35%** of households drank untreated groundwater while
about **50%** used RO-treated water. Use that to justify RO units as the contested resource and to
argue your pool size, rather than picking a number out of the air. Put the justification in
`src/sim/config.py` as a comment **and** in your report section.

Model the two resources differently — that is where the interesting negotiation lives:

| Resource | Character |
|---|---|
| **RO unit** | Durable, high value, serves a village for many months once placed. Allocate few, rarely. |
| **Water bowser** | Recurring monthly trips, cost scales with `distance_to_depot_km`. Allocate several, every month. |

## 4. Tasks

### Week 1–2 — toy demo (part of the shared foundation, pair with D on the logger)

- [ ] `src/sim/demo_contract_net.py`: 1 coordinator + 3 villages, hard-coded bids, one round.
- [ ] Runs end to end over SPADE's built-in XMPP server and **writes `logs/messages.csv`**.
- [ ] Verify and record the exact commands in `CLAUDE.md`:
      ```
      spade run                              # terminal 1, leave running
      python -m src.sim.demo_contract_net    # terminal 2
      ```
- [ ] On Windows, SPADE + asyncio is the most likely place to lose a day. If it fights you, run it
      under WSL (Ubuntu) as START_HERE suggests, and tell the team which you used.

### Week 3–4 — the CFP state machine

- [ ] Coordinator as an explicit state machine: `IDLE → CFP_SENT → COLLECTING → AWARDING → CONFIRMING → DONE`.
- [ ] **Every `receive()` and every CFP deadline has a timeout. Never block forever.** A village that
      goes silent must not stall the month — treat the missing reply as a refuse, and log that you did.
- [ ] Thread id per negotiation so D can reconstruct one full exchange from `messages.csv`.
- [ ] A documented tie-break for identical bids. Fixed seed, so it is reproducible.

### Week 5–6 — scarcity model and baselines

In `allocation.py`, three pure functions over the same inputs so they are directly comparable:

- [ ] `allocate_contract_net(bids, pool)` — your negotiated result.
- [ ] `allocate_equal_split(villages, pool)` — baseline 1: divide the pool evenly, ignoring risk.
- [ ] `allocate_first_come(bids, pool)` — baseline 2: serve in arrival order until the pool is empty.
- [ ] One shared metric so the comparison means something: **risk-weighted population served**
      (Σ risk × population over served villages). Agree the definition with D, who computes the
      evaluation. If the Contract Net does not beat both baselines on it, say so and investigate —
      a negative result honestly reported beats a fudged positive one.

### Week 7–8 — full negotiation

- [ ] Scale to all 11 VillageAgents and 12 simulated months.
- [ ] Carry state across months: a village with an RO unit placed last month needs less this month.
- [ ] Exercise `failure` and re-offer at least once in the demo run.
- [ ] Record per month: rounds used, messages sent, villages served, unserved high-risk villages.

## 5. Interfaces

```python
# you consume
bid(risk, population, distance_to_depot_km) -> float      # from A
risk_record = {"ds_division", "month", "wqi", "tier", ...} # from B
log_message(...)                                           # from D

# you publish — cfp payload (JSON, schema in src/core/ontology.py)
{"performative": "cfp", "thread": str, "month": int,
 "resource": "ro_unit" | "bowser", "n_available": int,
 "round": int, "deadline_s": float}

# you publish — logs/allocations.csv
month, resource, ds_division, round, winning_bid, method   # method: contract_net | equal_split | first_come
```

## 6. Rules that bite you specifically

- Every message between agents is logged: timestamp, sender, receiver, performative, thread id,
  payload. **The evaluation metrics are computed from that log** — an unlogged message is a hole in
  D's numbers.
- Fixed random seeds everywhere.
- Message bodies are JSON against D's schema in `src/core/ontology.py`. Do not invent a field
  locally — after the week-3 freeze, a schema change needs all four to agree.
- `src/core/allocation.py` must be testable **without XMPP**. The three allocators are plain
  functions over plain data.

## 7. Before you say a task is done

```
pytest -q
spade run                              # terminal 1
python -m src.sim.demo_contract_net    # terminal 2
```
Then show `logs/messages.csv` — the actual rows, with all six performatives present. Show the
command and its output, not a claim that it works.

## 8. Prompts that work in Claude Code

- `Read CLAUDE.md and docs/tasks/member_c_contract_net.md. Implement src/core/allocation.py with all three allocators and pytest tests. Pure functions only, no SPADE.`
- `Implement the coordinator state machine in src/agents/resource_coordinator.py with a timeout on every receive and every CFP deadline. Use the schema in src/core/ontology.py.`
- `Run the toy demo and show me logs/messages.csv. Confirm cfp, propose, refuse, accept-proposal, reject-proposal and inform all appear.`
