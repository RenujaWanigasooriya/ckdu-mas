"""RiskScoringAgent demo: stub WellMonitor -> RiskScoringAgent -> stub subscriber.

The feeder sends one ``well_readings`` message per DS division for each simulated month
(synthetic wells, source="synthetic"). RiskScoringAgent replies with one ``risk_record`` per
message. Every message is validated and logged to logs/messages.csv; the full village detail
(share of wells Poor or worse, worst tier, parameters used) goes to logs/risk_scores.csv.

The feeder and subscriber are STUBS standing in for Member A's WellMonitorAgent and for the
Coordinator / Alert / Hotspot agents.

Run (XMPP server in another terminal: `spade run --host localhost --memory`):
    python -m src.sim.demo_risk_scoring
or with SPADE's in-process server:
    python -m src.sim.demo_risk_scoring --embedded-server
"""
from __future__ import annotations

import argparse
import asyncio
import time
import uuid
from pathlib import Path

import pandas as pd
import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour

from src.agents import common
from src.agents.risk_scoring import RiskScoringAgent
from src.core import ontology, risk_tiers, wqi
from src.sim import load_data

DOMAIN = "localhost"
PASSWORD = "demo"
DEMO_MONTHS = [1, 7]  # calendar months: January (Wet) and July (Dry)
COLLECT_TIMEOUT_S = 30.0
RISK_SCORES_PATH = Path("logs") / "risk_scores.csv"


class StubWellMonitor(Agent):
    """Sends the monthly readings of each DS division to the risk scorer."""

    def __init__(self, jid, password, scorer: str, readings: pd.DataFrame, **kwargs):
        super().__init__(jid, password, **kwargs)
        self.scorer = scorer
        self.readings = readings

    class SendReadings(OneShotBehaviour):
        async def run(self):
            agent: StubWellMonitor = self.agent
            for month_index, month in enumerate(DEMO_MONTHS):
                month_rows = agent.readings[agent.readings["month"] == month]
                for ds, rows in month_rows.groupby("ds_division", sort=True):
                    body = {"type": "well_readings", "month_index": month_index,
                            "ds_division": ds, "source": "synthetic",
                            "readings": rows.to_dict(orient="records")}
                    await common.send(self, agent.scorer, ontology.INFORM, body,
                                      f"wr-{month_index}-{uuid.uuid4().hex[:6]}")

    async def setup(self):
        self.add_behaviour(self.SendReadings())


class StubSubscriber(Agent):
    """Collects risk_record messages until it has ``expected`` or the timeout passes."""

    def __init__(self, jid, password, expected: int, **kwargs):
        super().__init__(jid, password, **kwargs)
        self.expected = expected
        self.records: list[dict] = []

    class Collect(OneShotBehaviour):
        async def run(self):
            agent: StubSubscriber = self.agent
            deadline = time.monotonic() + COLLECT_TIMEOUT_S
            while len(agent.records) < agent.expected:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                got = await common.receive(self, timeout=remaining)
                if got and got[2]["type"] == "risk_record":
                    agent.records.append(got[2])

    async def setup(self):
        self.add_behaviour(self.Collect())


async def main() -> None:
    method_frame = load_data.load_wqi_method()
    method = wqi.method_from_frame(method_frame)
    classes = risk_tiers.classes_from_frame(method_frame)
    readings = load_data.load_monthly_readings()
    n_divisions = readings["ds_division"].nunique()

    sink = StubSubscriber(f"risk_subscriber@{DOMAIN}", PASSWORD,
                          expected=n_divisions * len(DEMO_MONTHS))
    scorer = RiskScoringAgent(f"risk_scoring@{DOMAIN}", PASSWORD, subscribers=[str(sink.jid)],
                              method=method, classes=classes)
    feeder = StubWellMonitor(f"well_monitor@{DOMAIN}", PASSWORD, scorer=str(scorer.jid),
                             readings=readings)
    await sink.start(auto_register=True)
    await scorer.start(auto_register=True)
    await feeder.start(auto_register=True)

    collect = next(iter(sink.behaviours))
    await asyncio.wait_for(collect.join(), timeout=COLLECT_TIMEOUT_S + 10)

    for agent in (feeder, scorer, sink):
        await agent.stop()

    detail = pd.DataFrame(scorer.history)
    RISK_SCORES_PATH.parent.mkdir(parents=True, exist_ok=True)
    detail.to_csv(RISK_SCORES_PATH, index=False)

    got = pd.DataFrame(sink.records).sort_values(["month_index", "ds_division"])
    print(f"risk_records received: {len(got)} of {sink.expected}")
    print(got[["month_index", "ds_division", "wqi", "tier", "drivers"]].to_string(index=False))
    print(f"\nwrote {RISK_SCORES_PATH} ({len(detail)} rows); messages in logs/messages.csv")
    print("Risk indicator from published water-quality thresholds - not a CKDu diagnosis.")
    if len(got) < sink.expected:
        raise RuntimeError(f"only {len(got)} of {sink.expected} risk_records arrived before the timeout")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--embedded-server", action="store_true",
                    help="start SPADE's in-process XMPP server instead of using `spade run`")
    spade.run(main(), embedded_xmpp_server=ap.parse_args().embedded_server)
