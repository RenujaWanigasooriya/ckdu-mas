"""Generate SYNTHETIC well readings calibrated to the real area statistics
in ckdu_01_water_quality_area_stats.csv (Cooray et al. 2019, Table 1).

Every row is labelled source="synthetic". Do not present these as measured data.

Method: for each prevalence class, season and parameter, a Beta distribution is
scaled onto [min, max] so that its mean equals the published average. A single
latent factor links the parameters within one well (so hardness, EC, F tend to
move together). The strength of that link (RHO) is an assumption, not a
published value.

Usage:
    python generate_synthetic_wells.py --wells-per-ds 20 --seed 42
"""
import argparse
import numpy as np
import pandas as pd
from scipy import stats

PARAMS = ["pH", "EC_uS_cm", "alkalinity_mg_L", "hardness_mg_L", "F_mg_L",
          "DOC_mg_L", "Cl_mg_L", "SO4_mg_L", "Fe_ug_L"]
CONCENTRATION = 4.0   # Beta "sample size"; lower = more spread
RHO = 0.6             # assumed correlation between parameters within a well


def beta_for(lo, hi, mean):
    m = (mean - lo) / (hi - lo)
    m = min(max(m, 0.02), 0.98)
    return m * CONCENTRATION, (1 - m) * CONCENTRATION


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stats", default="data/raw/ckdu_01_water_quality_area_stats.csv")
    ap.add_argument("--design", default="data/raw/ckdu_03_sampling_design_ds_divisions.csv")
    ap.add_argument("--wells-per-ds", type=int, default=20)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="data/processed/synthetic_wells.csv")
    a = ap.parse_args()

    rng = np.random.default_rng(a.seed)
    st = pd.read_csv(a.stats)
    design = pd.read_csv(a.design)

    rows = []
    for _, ds in design.iterrows():
        cls = ds["ckdu_prevalence_class"]
        for w in range(a.wells_per_ds):
            well_id = f"{ds['ds_division'][:3].upper()}-{w + 1:03d}"
            shared = rng.standard_normal()
            for season in ["Wet", "Dry"]:
                row = {"well_id": well_id, "ds_division": ds["ds_division"],
                       "district": ds["district"], "ckdu_prevalence_class": cls,
                       "season": season, "source": "synthetic"}
                sub = st[(st.ckdu_prevalence_class == cls) & (st.season == season)]
                for p in PARAMS:
                    lo = float(sub[sub.statistic == "Min"][p].iloc[0])
                    hi = float(sub[sub.statistic == "Max"][p].iloc[0])
                    mean = float(sub[sub.statistic == "Avg"][p].iloc[0])
                    al, be = beta_for(lo, hi, mean)
                    z = RHO * shared + np.sqrt(1 - RHO ** 2) * rng.standard_normal()
                    u = stats.norm.cdf(z)
                    row[p] = round(lo + (hi - lo) * stats.beta.ppf(u, al, be), 2)
                rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(a.out, index=False)
    print(f"Wrote {len(out)} synthetic readings to {a.out}")


if __name__ == "__main__":
    main()
