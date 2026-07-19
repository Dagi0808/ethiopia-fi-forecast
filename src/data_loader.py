"""
data_loader.py
--------------
Utilities for loading and validating the Ethiopia FI unified dataset.
All raw files live in data/raw/; processed outputs go to data/processed/.
"""

import logging
import os
import pandas as pd

logger = logging.getLogger(__name__)

# ── paths ──────────────────────────────────────────────────────────────────────
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

MAIN_FILE = os.path.join(RAW_DIR, "ethiopia_fi_unified_data.xlsx")
REF_FILE  = os.path.join(RAW_DIR, "reference_codes.xlsx")

REQUIRED_COLUMNS = [
    "record_id", "record_type", "indicator_code", "value_numeric", "observation_date"
]


def _validate_file(path: str) -> None:
    """Raise FileNotFoundError with a clear message if path does not exist."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Required data file not found: {path}\n"
            f"Make sure you have placed the raw data files in data/raw/"
        )


def _validate_columns(df: pd.DataFrame, required: list, source: str) -> None:
    """Warn about any missing expected columns."""
    missing = [c for c in required if c not in df.columns]
    if missing:
        logger.warning("File '%s' is missing expected columns: %s", source, missing)


def load_main_dataset() -> pd.DataFrame:
    """
    Load the primary unified dataset (observations + events + targets).

    Returns
    -------
    pd.DataFrame
        All rows from the 'ethiopia_fi_unified_data' sheet with
        observation_date parsed as datetime.

    Raises
    ------
    FileNotFoundError
        If the raw Excel file is not present in data/raw/.
    ValueError
        If the expected sheet is not found inside the file.
    """
    _validate_file(MAIN_FILE)
    try:
        df = pd.read_excel(MAIN_FILE, sheet_name="ethiopia_fi_unified_data")
    except Exception as exc:
        raise ValueError(
            f"Could not read sheet 'ethiopia_fi_unified_data' from {MAIN_FILE}. "
            f"Original error: {exc}"
        ) from exc

    _validate_columns(df, REQUIRED_COLUMNS, MAIN_FILE)

    df["observation_date"] = pd.to_datetime(df["observation_date"], errors="coerce")
    # collection_date may have mixed types — coerce silently with explicit format
    df["collection_date"] = pd.to_datetime(
        df["collection_date"].astype(str), format="mixed", errors="coerce"
    )
    logger.info("Loaded main dataset: %d rows, %d columns", *df.shape)
    return df


def load_impact_links() -> pd.DataFrame:
    """
    Load the impact_link records from the Impact_sheet tab.

    Returns
    -------
    pd.DataFrame
        Impact link rows (parent_id links back to events in the main sheet).

    Raises
    ------
    FileNotFoundError
        If the raw Excel file is not present.
    ValueError
        If the Impact_sheet tab is missing.
    """
    _validate_file(MAIN_FILE)
    try:
        df = pd.read_excel(MAIN_FILE, sheet_name="Impact_sheet")
    except Exception as exc:
        raise ValueError(
            f"Could not read sheet 'Impact_sheet' from {MAIN_FILE}. "
            f"Original error: {exc}"
        ) from exc

    df["observation_date"] = pd.to_datetime(df["observation_date"], errors="coerce")
    logger.info("Loaded impact links: %d rows", len(df))
    return df


def load_reference_codes() -> pd.DataFrame:
    """
    Load the reference codes / data dictionary.

    Returns
    -------
    pd.DataFrame
        Valid codes for every categorical field in the unified schema.

    Raises
    ------
    FileNotFoundError
        If the reference codes file is not present.
    """
    _validate_file(REF_FILE)
    try:
        df = pd.read_excel(REF_FILE, sheet_name="reference_codes")
    except Exception as exc:
        raise ValueError(
            f"Could not read 'reference_codes' sheet from {REF_FILE}. "
            f"Original error: {exc}"
        ) from exc

    logger.info("Loaded reference codes: %d rows", len(df))
    return df


def split_by_record_type(df: pd.DataFrame) -> dict:
    """
    Split the unified dataframe by record_type.

    Parameters
    ----------
    df : pd.DataFrame
        Full unified dataset (output of load_main_dataset).

    Returns
    -------
    dict  {record_type: DataFrame}
        Keys match values found in df['record_type'].
    """
    if "record_type" not in df.columns:
        raise KeyError("DataFrame does not have a 'record_type' column.")
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
    main   = load_main_dataset()
    impact = load_impact_links()
    ref    = load_reference_codes()
    split  = split_by_record_type(main)

    result = {
        "main":         main,
        "observations": split.get("observation", pd.DataFrame()),
        "events":       split.get("event",       pd.DataFrame()),
        "targets":      split.get("target",      pd.DataFrame()),
        "impact_links": impact,
        "reference":    ref,
    }
    logger.info(
        "load_all complete — obs=%d events=%d targets=%d impact_links=%d",
        len(result["observations"]), len(result["events"]),
        len(result["targets"]),     len(result["impact_links"]),
    )
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    data = load_all()
    for k, v in data.items():
        print(f"{k:15s} → {v.shape}")
