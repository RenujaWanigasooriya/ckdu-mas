import pandas as pd
import pytest

from src.core import wells
from src.core.geo import distance_to_depot_km
from src.sim import load_data


def _seasonal(source="synthetic"):
    base = {"well_id": "PAD-001", "ds_division": "Padaviya", "district": "Anuradhapura",
            "ckdu_prevalence_class": "High", "source": source}
    params = {p: 1.0 for p in wells.PARAMS}
    return pd.DataFrame([{**base, "season": "Wet", **params}, {**base, "season": "Dry", **params}])


def test_month_season_mapping_covers_year():
    assert sorted(wells.MONTH_TO_SEASON) == list(range(1, 13))
    assert wells.season_for_month(11) == "Wet"
    assert wells.season_for_month(7) == "Dry"
    with pytest.raises(ValueError):
        wells.season_for_month(13)


def test_expand_to_months_gives_twelve_rows_per_well():
    out = wells.expand_to_months(_seasonal())
    assert list(out.columns) == wells.READING_COLUMNS
    assert sorted(out["month"]) == list(range(1, 13))
    assert (out["season"] == out["month"].map(wells.MONTH_TO_SEASON)).all()


def test_mixed_sources_rejected_unless_explicit():
    mixed = pd.concat([_seasonal("synthetic"), _seasonal("real").assign(well_id="REAL-1")])
    with pytest.raises(wells.MixedSourceError):
        wells.check_sources(mixed)
    wells.check_sources(mixed, allow_mixed=True)
    assert set(wells.real_only(mixed)["source"]) == {"real"}
    assert set(wells.synthetic_only(mixed)["source"]) == {"synthetic"}


def test_unlabelled_or_unknown_source_rejected():
    with pytest.raises(ValueError):
        wells.check_sources(_seasonal().drop(columns="source"))
    with pytest.raises(ValueError):
        wells.check_sources(_seasonal("guess"))


def test_validate_rejects_missing_column_and_bad_values():
    good = wells.expand_to_months(_seasonal())
    with pytest.raises(ValueError, match="missing"):
        wells.validate_readings(good.drop(columns="F_mg_L"))
    with pytest.raises(ValueError, match="negative"):
        wells.validate_readings(good.assign(F_mg_L=-1.0))
    with pytest.raises(ValueError, match="season"):
        wells.validate_readings(good.assign(season="Wet"))


def test_synthetic_wells_file_loads_as_monthly_frame():
    df = load_data.load_monthly_readings()
    assert list(df.columns) == wells.READING_COLUMNS
    assert set(df["source"]) == {"synthetic"}
    assert len(df) == 11 * 20 * 12


def test_ds_divisions_complete_and_distances_match_coordinates():
    ds = load_data.load_ds_divisions()
    assert len(ds) == 11
    assert ds["population"].gt(0).all()
    for _, r in ds.iterrows():
        assert r["distance_to_depot_km"] == pytest.approx(distance_to_depot_km(r["lat"], r["lon"]), abs=0.05)


def test_loaders_fail_loudly(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_data.load_area_stats(tmp_path / "nope.csv")
    empty = tmp_path / "empty.csv"
    empty.write_text("")
    with pytest.raises(ValueError):
        load_data.load_area_stats(empty)
    bad = tmp_path / "bad.csv"
    bad.write_text("a,b\n1,2\n")
    with pytest.raises(ValueError, match="missing columns"):
        load_data.load_area_stats(bad)


def test_all_raw_loaders_read_real_files():
    assert len(load_data.load_area_stats()) == 30
    assert not load_data.load_wqi_method().empty
    assert not load_data.load_aggregate_stats().empty
    assert not load_data.load_validation_benchmarks().empty
