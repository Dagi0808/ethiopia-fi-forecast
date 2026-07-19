"""
tests/test_data_loader.py
--------------------------
Unit tests for data loading and enrichment modules.
Run with: python -m pytest tests/ -v
"""

import os
import sys
import pytest
import pandas as pd

# make src importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data_loader import load_main_dataset, load_impact_links, load_reference_codes, load_all, split_by_record_type


# ── data_loader tests ──────────────────────────────────────────────────────────

class TestLoadMainDataset:
    def test_returns_dataframe(self):
        df = load_main_dataset()
        assert isinstance(df, pd.DataFrame)

    def test_has_expected_columns(self):
        df = load_main_dataset()
        required = ["record_id", "record_type", "indicator_code", "value_numeric", "observation_date"]
        for col in required:
            assert col in df.columns, f"Missing column: {col}"

    def test_record_count(self):
        df = load_main_dataset()
        assert len(df) >= 43, "Expected at least 43 records in raw dataset"

    def test_record_types_present(self):
        df = load_main_dataset()
        types = df["record_type"].unique()
        assert "observation" in types
        assert "event" in types
        assert "target" in types

    def test_observation_date_is_datetime(self):
        df = load_main_dataset()
        assert pd.api.types.is_datetime64_any_dtype(df["observation_date"])

    def test_no_duplicate_record_ids(self):
        df = load_main_dataset()
        assert df["record_id"].dropna().duplicated().sum() == 0, "Duplicate record_ids found"


class TestLoadImpactLinks:
    def test_returns_dataframe(self):
        df = load_impact_links()
        assert isinstance(df, pd.DataFrame)

    def test_has_parent_id_column(self):
        df = load_impact_links()
        assert "parent_id" in df.columns

    def test_minimum_links(self):
        df = load_impact_links()
        assert len(df) >= 14, "Expected at least 14 impact links"

    def test_all_parent_ids_are_events(self):
        """Every parent_id in impact_links must reference an event in the main dataset."""
        impact = load_impact_links()
        main = load_main_dataset()
        event_ids = set(main[main["record_type"] == "event"]["record_id"].dropna())
        for pid in impact["parent_id"].dropna():
            assert pid in event_ids, f"Orphaned parent_id: {pid}"


class TestLoadReferenceCodes:
    def test_returns_dataframe(self):
        df = load_reference_codes()
        assert isinstance(df, pd.DataFrame)

    def test_has_required_columns(self):
        df = load_reference_codes()
        for col in ["field", "code", "description"]:
            assert col in df.columns

    def test_record_type_codes_exist(self):
        df = load_reference_codes()
        rt_codes = df[df["field"] == "record_type"]["code"].tolist()
        assert "observation" in rt_codes
        assert "event" in rt_codes
        assert "impact_link" in rt_codes


class TestSplitByRecordType:
    def test_returns_dict(self):
        df = load_main_dataset()
        result = split_by_record_type(df)
        assert isinstance(result, dict)

    def test_keys_match_record_types(self):
        df = load_main_dataset()
        result = split_by_record_type(df)
        for key in result:
            assert key in ["observation", "event", "target", "impact_link", "baseline", "forecast"]

    def test_counts_add_up(self):
        df = load_main_dataset()
        result = split_by_record_type(df)
        total = sum(len(v) for v in result.values())
        assert total == len(df)


class TestLoadAll:
    def test_returns_all_keys(self):
        data = load_all()
        for key in ["main", "observations", "events", "targets", "impact_links", "reference"]:
            assert key in data, f"Missing key: {key}"

    def test_observations_are_subset_of_main(self):
        data = load_all()
        obs_ids = set(data["observations"]["record_id"].dropna())
        main_ids = set(data["main"]["record_id"].dropna())
        assert obs_ids.issubset(main_ids)

    def test_findex_anchor_points_present(self):
        """The 5 core Findex survey data points must be present."""
        data = load_all()
        obs = data["observations"]
        acc = obs[obs["indicator_code"] == "ACC_OWNERSHIP"]
        dates = pd.to_datetime(acc["observation_date"]).dt.year.tolist()
        for year in [2014, 2017, 2021, 2024]:
            assert year in dates, f"Missing Findex year: {year}"

    def test_events_have_no_pillar(self):
        """Events must NOT have a pillar assigned (per schema design principle)."""
        data = load_all()
        events = data["events"]
        # pillar should be null/NaN for events
        non_null = events["pillar"].dropna()
        assert len(non_null) == 0, f"Events with pillar assigned: {non_null.tolist()}"


# ── enrichment tests ───────────────────────────────────────────────────────────

class TestEnrichedData:
    """Tests that run against the processed enriched CSV if it exists."""

    ENRICHED_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "processed", "ethiopia_fi_enriched.csv"
    )

    def test_enriched_file_exists(self):
        assert os.path.exists(self.ENRICHED_PATH), "Run src/enrich_data.py first"

    def test_enriched_has_more_records(self):
        if not os.path.exists(self.ENRICHED_PATH):
            pytest.skip("Enriched file not found")
        df = pd.read_csv(self.ENRICHED_PATH)
        assert len(df) > 43, "Enriched dataset should have more than 43 records"

    def test_findex_2011_baseline_added(self):
        if not os.path.exists(self.ENRICHED_PATH):
            pytest.skip("Enriched file not found")
        df = pd.read_csv(self.ENRICHED_PATH)
        acc_2011 = df[
            (df["indicator_code"] == "ACC_OWNERSHIP") &
            (df["observation_date"].astype(str).str.startswith("2011"))
        ]
        assert len(acc_2011) > 0, "Findex 2011 baseline (14%) should be in enriched dataset"

    def test_usage_digital_payment_added(self):
        if not os.path.exists(self.ENRICHED_PATH):
            pytest.skip("Enriched file not found")
        df = pd.read_csv(self.ENRICHED_PATH)
        usg = df[df["indicator_code"] == "USG_DIGITAL_PAYMENT"]
        assert len(usg) >= 2, "Digital payment observations for 2021 and 2024 should exist"

    def test_no_event_has_pillar(self):
        if not os.path.exists(self.ENRICHED_PATH):
            pytest.skip("Enriched file not found")
        df = pd.read_csv(self.ENRICHED_PATH)
        events = df[df["record_type"] == "event"]
        non_null = events["pillar"].dropna()
        assert len(non_null) == 0, "Events must not have pillar assigned"
