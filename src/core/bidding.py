"""VillageAgent bid function. Pure module: no SPADE imports.

First draft (START_HERE): need = risk x population / distance_to_depot_km.

Design decisions (record every change to this function here, with the reason):
- Distance is clamped to MIN_DISTANCE_KM so a village at the depot does not divide by zero
  or receive an unbounded bid.
- Population 0 means nobody to serve, so the bid is 0. A missing population or distance raises:
  the caller (VillageAgent) must refuse the CFP rather than bid on a guessed value.
- Raw bids differ by orders of magnitude between villages, so the coordinator compares
  ``normalise_bids`` output in [0, 1] instead.
- Ties are broken by ds_division name (alphabetical) in ``rank_bids`` so allocation is
  deterministic and reproducible.
"""
from __future__ import annotations

import math
from collections.abc import Mapping

MIN_DISTANCE_KM = 1.0


def _is_missing(x) -> bool:
    return x is None or (isinstance(x, float) and math.isnan(x))


def bid(risk: float, population: int, distance_to_depot_km: float) -> float:
    """Raw need score for one village: risk x population / max(distance, MIN_DISTANCE_KM)."""
    if _is_missing(risk):
        raise ValueError("risk is missing")
    if _is_missing(population):
        raise ValueError("population is missing")
    if _is_missing(distance_to_depot_km):
        raise ValueError("distance_to_depot_km is missing")
    if risk < 0:
        raise ValueError(f"risk must be >= 0, got {risk}")
    if population < 0:
        raise ValueError(f"population must be >= 0, got {population}")
    if distance_to_depot_km < 0:
        raise ValueError(f"distance_to_depot_km must be >= 0, got {distance_to_depot_km}")

    if population == 0 or risk == 0:
        return 0.0
    return float(risk) * float(population) / max(float(distance_to_depot_km), MIN_DISTANCE_KM)


def normalise_bids(raw: Mapping[str, float]) -> dict[str, float]:
    """Scale raw bids into [0, 1] by dividing by the largest bid. All-zero input stays zero."""
    for name, value in raw.items():
        if _is_missing(value) or value < 0:
            raise ValueError(f"bid for {name!r} must be a number >= 0, got {value!r}")
    top = max(raw.values(), default=0.0)
    if top == 0:
        return {name: 0.0 for name in raw}
    return {name: value / top for name, value in raw.items()}


def rank_bids(bids: Mapping[str, float]) -> list[tuple[str, float]]:
    """Highest bid first; equal bids ordered by ds_division name (the documented tie-break)."""
    return sorted(bids.items(), key=lambda kv: (-kv[1], kv[0]))
