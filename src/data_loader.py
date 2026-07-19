"""
data_loader.py
--------------
Utilities for loading and validating the Ethiopia FI unified dataset.
All raw files live in data/raw/; processed outputs go to data/processed/.
"""

import os
import pandas as pd

# ── paths ──────────────────────────────────────────────────────────────────────
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

MAIN_FILE = os.path.join(RAW_DIR, "ethiopia_fi_unified_data.xlsx")
REF_FILE  = os.path.join(RAW_DIR, "reference_codes.xlsx")


def load_main_dataset() -> pd.DataFrame:
    """
    Load the primary unified dataset (observations + events + targets).

    Returns
    -------
    pd.DataFrame
        All rows from the 'ethiopia_fi_unified_data' sheet with
        observation_date parsed as datetime.
    """
    df = pd.read_excel(MAIN_FILE, sheet_name="ethiopia_fi_unified_data")
    df["observation_date"] = pd.to_datetime(df["observation_date"], errors="coerce")
    df["collection_date"]  = pd.to_datetime(df["collection_date"],  errors="coerce")
    return df


def load_impact_links() -> pd.DataFrame:
    """
    Load the impact_link records from the Impact_sheet tab.

    Returns
    -------
    pd.DataFrame
        Impact link rows (parent_id links back to events in the main sheet).
    """
    df = pd.read_excel(MAIN_FILE, sheet_name="Impact_sheet")
    df["observation_date"] = pd.to_datetime(df["observation_date"], errors="coerce")
    return df


def load_reference_codes() -> pd.DataFrame:
    """
    Load the reference codes / data dictionary.

    Returns
    -------
    pd.DataFrame
        Valid codes for every categorical field in the unified schema.
    """
    return pd.read_excel(REF_FILE, sheet_name="reference_codes")


def split_by_record_type(df: pd.DataFrame) -> dict:
    """
    Convenience function — split the unified dataframe by record_type.

    Parameters
    ----------
    df : pd.DataFrame
        Full unified dataset (output of load_main_dataset).

    Returns
    -------
    dict  {record_type: DataFrame}
        Keys: 'observation', 'event', 'target'
    """
    return {rt: df[df["record_type"] == rt].copy() for rt in df["record_type"].unique()}


def load_all() -> dict:
    """
    Load every dataset in one call.

    Returns
    -------
    dict with keys:
        'main'         — full unified dataset
        'observations' — only observation rows
        'events'       — only event rows
        'targets'      — only target rows
        'impact_links' — impact link rows
        'reference'    — reference codes
    """
    main    = load_main_dataset()
    impact  = load_impact_links()
    ref     = load_reference_codes()
    split   = split_by_record_type(main)

    return {
        "main":         main,
        "observations": split.get("observation", pd.DataFrame()),
        "events":       split.get("event",       pd.DataFrame()),
        "targets":      split.get("target",      pd.DataFrame()),
        "impact_links": impact,
        "reference":    ref,
    }


if __name__ == "__main__":
    data = load_all()
    for k, v in data.items():
        print(f"{k:15s} → {v.shape}")
