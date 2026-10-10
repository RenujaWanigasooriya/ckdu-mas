"""VillageAgent: one per DS division. Holds only its own data, bids on CFPs.

No agent sees the full picture: a village knows its own population, depot distance and current
risk, nothing about the other villages. Bid logic lives in src/core/bidding.py.
"""
from __future__ import annotations

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

from src.agents import common
from src.core import bidding, ontology

CFP_WAIT_S = 30.0      # how long to wait for the next CFP before checking again
DECISION_MARGIN_S = 5.0  # extra wait for accept/reject beyond the CFP deadline


class VillageAgent(Agent):
    def __init__(
        self,
        jid: str,
        password: str,
        ds_division: str,
        population: int,
        distance_to_depot_km: float,
        **kwargs,
    ):
        super().__init__(jid, password, **kwargs)
        self.ds_division = ds_division
        self.population = population
        self.distance_to_depot_km = distance_to_depot_km
        self.risk: float | None = None
        self.risk_tier: str | None = None
        self.allocations: list[dict] = []

    def set_risk(self, risk: float, tier: str) -> None:
        """Updated from RiskScoringAgent output (or a stub until Member B's agent exists)."""
        self.risk, self.risk_tier = risk, tier

    def raw_bid(self) -> float:
        return bidding.bid(self.risk, self.population, self.distance_to_depot_km)

    class RespondToCfp(CyclicBehaviour):
        async def run(self):
            got = await common.receive(self, timeout=CFP_WAIT_S)
            if got is None:
                return
            msg, performative, body = got
            if performative != ontology.CFP:
                return  # stray accept/reject from an earlier round; already logged
            await self.handle_cfp(msg, body)

        async def handle_cfp(self, msg, cfp):
            agent: VillageAgent = self.agent
            coordinator = str(msg.sender)
            base = {"month_index": cfp["month_index"], "round": cfp["round"],
                    "ds_division": agent.ds_division}
            try:
                raw = agent.raw_bid() if agent.risk is not None else 0.0
            except ValueError as exc:
                await common.send(self, coordinator, ontology.REFUSE,
                                  {"type": "refuse", **base, "reason": f"cannot compute bid: {exc}"},
                                  msg.thread)
                return
            if raw <= 0:
                await common.send(self, coordinator, ontology.REFUSE,
                                  {"type": "refuse", **base, "reason": "no need this month"},
                                  msg.thread)
                return

            # The coordinator normalises across villages; a village only knows its own raw score.
            await common.send(self, coordinator, ontology.PROPOSE, {
                "type": "propose", **base, "bid": raw,
                "risk_tier": agent.risk_tier or "unknown", "population": int(agent.population),
            }, msg.thread)

            got = await common.receive(self, timeout=cfp["deadline_s"] + DECISION_MARGIN_S)
            if got is None:
                print(f"[{agent.ds_division}] no decision before timeout; giving up this round")
                return
            reply, performative, decision = got
            if performative == ontology.ACCEPT_PROPOSAL:
                agent.allocations.append(decision)
                await common.send(self, coordinator, ontology.INFORM, {
                    "type": "inform_done", **base,
                    "resource": decision["resource"], "units": decision["units"],
                }, reply.thread)

    async def setup(self):
        self.add_behaviour(self.RespondToCfp())
