"""
enrich_data.py
--------------
Adds new observations, events, and impact_links to the unified dataset.
All additions are documented inline and summarised in data/data_enrichment_log.md.

Run: python -m src.enrich_data
Outputs:
    data/processed/ethiopia_fi_enriched.csv
    data/processed/impact_links_enriched.csv
"""

import logging
import os
import pandas as pd

logger = logging.getLogger(__name__)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


# ── helpers ────────────────────────────────────────────────────────────────────

def _next_id(df: pd.DataFrame, prefix: str) -> str:
    """Generate the next sequential record_id for a given prefix (e.g. 'REC_', 'EVT_', 'IMP_')."""
    existing = df["record_id"].dropna().astype(str)
    nums = [
        int(r.replace(prefix, ""))
        for r in existing
        if r.startswith(prefix) and r.replace(prefix, "").isdigit()
    ]
    return f"{prefix}{(max(nums) + 1 if nums else 1):04d}"


def _blank_row(df: pd.DataFrame) -> pd.Series:
    """Return a Series with all columns from df set to None."""
    return pd.Series({col: None for col in df.columns})


def _add_obs(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """Append one observation row to df and return the updated DataFrame."""
    row = _blank_row(df)
    row["record_type"]  = "observation"
    row["collected_by"] = "Dag Dagne"
    row["collection_date"] = "2026-07-19"
    for k, v in kwargs.items():
        if k not in df.columns:
            logger.warning("Field '%s' not in schema — skipping", k)
            continue
        row[k] = v
    row["record_id"] = _next_id(df, "REC_")
    return pd.concat([df, row.to_frame().T], ignore_index=True)


def _add_event(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """Append one event row to df. pillar is always left NULL per schema design."""
    row = _blank_row(df)
    row["record_type"]  = "event"
    row["pillar"]       = None   # events must NOT be pre-assigned a pillar
    row["collected_by"] = "Dag Dagne"
    row["collection_date"] = "2026-07-19"
    for k, v in kwargs.items():
        if k == "pillar":
            logger.warning("Attempted to set pillar on an event — blocked by schema rule")
            continue
        if k not in df.columns:
            logger.warning("Field '%s' not in schema — skipping", k)
            continue
        row[k] = v
    row["record_id"] = _next_id(df, "EVT_")
    return pd.concat([df, row.to_frame().T], ignore_index=True)


def _add_link(impact_df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """Append one impact_link row to impact_df."""
    row = _blank_row(impact_df)
    row["record_type"]  = "impact_link"
    row["collected_by"] = "Dag Dagne"
    row["collection_date"] = "2026-07-19"
    for k, v in kwargs.items():
        if k not in impact_df.columns:
            logger.warning("Impact field '%s' not in schema — skipping", k)
            continue
        row[k] = v
    row["record_id"] = _next_id(impact_df, "IMP_")
    return pd.concat([impact_df, row.to_frame().T], ignore_index=True)


def _validate_enrichment(main_df: pd.DataFrame, impact_df: pd.DataFrame) -> list:
    """
    Run post-enrichment validation checks.
    Returns a list of warning strings (empty = all good).
    """
    warnings = []

    # No duplicate record IDs
    dup_main = main_df["record_id"].dropna()[main_df["record_id"].dropna().duplicated()]
    if not dup_main.empty:
        warnings.append(f"Duplicate record_ids in main: {dup_main.tolist()}")

    # Events must have NULL pillar
    events = main_df[main_df["record_type"] == "event"]
    with_pillar = events["pillar"].dropna()
    if not with_pillar.empty:
        warnings.append(f"{len(with_pillar)} events have pillar set — violates schema")

    # All impact parent_ids must reference an existing event
    event_ids = set(main_df[main_df["record_type"] == "event"]["record_id"].dropna())
    orphans = [p for p in impact_df["parent_id"].dropna() if p not in event_ids]
    if orphans:
        warnings.append(f"Orphaned parent_ids in impact links: {orphans}")

    # Numeric values must be numeric where present
    non_numeric = main_df[
        main_df["value_numeric"].notna() &
        ~main_df["value_numeric"].apply(lambda x: isinstance(x, (int, float)))
    ]
    if not non_numeric.empty:
        warnings.append(f"{len(non_numeric)} rows have non-numeric value_numeric")

    return warnings


# ── New observations ────────────────────────────────────────────────────────────

NEW_OBSERVATIONS = [
    dict(
        indicator="Account Ownership Rate", indicator_code="ACC_OWNERSHIP",
        indicator_direction="higher_better", value_numeric=14.0,
        value_type="percentage", unit="%", observation_date="2011-12-31",
        pillar="ACCESS", gender="all", location="national",
        source_name="Global Findex 2011", source_type="survey",
        source_url="https://www.worldbank.org/en/publication/globalfindex",
        confidence="high",
        original_text="14% of adults in Ethiopia had an account at a formal financial institution in 2011.",
        notes="2011 Findex baseline — anchor point for 13-year trend. Was missing from starter dataset.",
    ),
    dict(
        indicator="Account Ownership Rate — Female", indicator_code="ACC_OWNERSHIP_F",
        indicator_direction="higher_better", value_numeric=16.0,
        value_type="percentage", unit="%", observation_date="2014-12-31",
        pillar="GENDER", gender="female", location="national",
        source_name="Global Findex 2014 microdata", source_type="survey",
        source_url="https://microdata.worldbank.org/index.php/catalog/2485",
        confidence="high",
        original_text="Female account ownership Ethiopia 2014: ~16% (Findex microdata).",
        notes="Enables gender gap trend from 2014. Gap 2014 = 28-16 = 12pp.",
    ),
    dict(
        indicator="Account Ownership Rate — Male", indicator_code="ACC_OWNERSHIP_M",
        indicator_direction="higher_better", value_numeric=28.0,
        value_type="percentage", unit="%", observation_date="2014-12-31",
        pillar="GENDER", gender="male", location="national",
        source_name="Global Findex 2014 microdata", source_type="survey",
        source_url="https://microdata.worldbank.org/index.php/catalog/2485",
        confidence="high",
        original_text="Male account ownership Ethiopia 2014: ~28% (Findex microdata).",
        notes="Paired with female 2014 to compute gender gap trend.",
    ),
    dict(
        indicator="Account Ownership Rate — Female", indicator_code="ACC_OWNERSHIP_F",
        indicator_direction="higher_better", value_numeric=27.0,
        value_type="percentage", unit="%", observation_date="2017-12-31",
        pillar="GENDER", gender="female", location="national",
        source_name="Global Findex 2017 microdata", source_type="survey",
        source_url="https://microdata.worldbank.org/index.php/catalog/3324",
        confidence="high",
        original_text="Female account ownership Ethiopia 2017: ~27% (Findex 2017).",
        notes="Gender gap widens to 16pp in 2017 — pre-mobile-money peak.",
    ),
    dict(
        indicator="Account Ownership Rate — Male", indicator_code="ACC_OWNERSHIP_M",
        indicator_direction="higher_better", value_numeric=43.0,
        value_type="percentage", unit="%", observation_date="2017-12-31",
        pillar="GENDER", gender="male", location="national",
        source_name="Global Findex 2017 microdata", source_type="survey",
        source_url="https://microdata.worldbank.org/index.php/catalog/3324",
        confidence="high",
        original_text="Male account ownership Ethiopia 2017: ~43% (Findex 2017).",
        notes="Enables full gender gap series: 2014(12pp) → 2017(16pp) → 2021(20pp) → 2024(18pp).",
    ),
    dict(
        indicator="Account Ownership Rate — Urban", indicator_code="ACC_OWNERSHIP_URB",
        indicator_direction="higher_better", value_numeric=68.0,
        value_type="percentage", unit="%", observation_date="2024-11-29",
        pillar="ACCESS", gender="all", location="urban",
        source_name="Global Findex 2024", source_type="survey",
        source_url="https://www.worldbank.org/en/publication/globalfindex/Report2024",
        confidence="high",
        original_text="Urban account ownership Ethiopia 2024: ~68%.",
        notes="Urban ownership 68% vs national 49% implies rural ~40%. Critical for rural inclusion analysis.",
    ),
    dict(
        indicator="Account Ownership Rate — Rural", indicator_code="ACC_OWNERSHIP_RUR",
        indicator_direction="higher_better", value_numeric=40.0,
        value_type="percentage", unit="%", observation_date="2024-11-29",
        pillar="ACCESS", gender="all", location="rural",
        source_name="Global Findex 2024", source_type="survey",
        source_url="https://www.worldbank.org/en/publication/globalfindex/Report2024",
        confidence="high",
        original_text="Rural account ownership Ethiopia 2024: ~40%.",
        notes="~80% of Ethiopians live rurally — rural gap is the primary inclusion barrier.",
    ),
    dict(
        indicator="Made or Received Digital Payment", indicator_code="USG_DIGITAL_PAYMENT",
        indicator_direction="higher_better", value_numeric=18.0,
        value_type="percentage", unit="%", observation_date="2021-12-31",
        pillar="USAGE", gender="all", location="national",
        source_name="Global Findex 2021", source_type="survey",
        source_url="https://www.worldbank.org/en/publication/globalfindex/Report2021",
        confidence="high",
        original_text="18% of Ethiopian adults made or received a digital payment in 2021.",
        notes="Usage baseline before Telebirr ramp-up. One of the two primary forecast targets.",
    ),
    dict(
        indicator="Made or Received Digital Payment", indicator_code="USG_DIGITAL_PAYMENT",
        indicator_direction="higher_better", value_numeric=35.0,
        value_type="percentage", unit="%", observation_date="2024-11-29",
        pillar="USAGE", gender="all", location="national",
        source_name="Global Findex 2024", source_type="survey",
        source_url="https://www.worldbank.org/en/publication/globalfindex/Report2024",
        confidence="high",
        original_text="~35% of Ethiopian adults made or received a digital payment in 2024.",
        notes="Primary forecast target for Usage dimension.",
    ),
    dict(
        indicator="Mobile Internet Penetration", indicator_code="ACC_MOBILE_INTERNET",
        indicator_direction="higher_better", value_numeric=28.0,
        value_type="percentage", unit="%", observation_date="2023-12-31",
        pillar="ACCESS", gender="all", location="national",
        source_name="GSMA Mobile Economy Sub-Saharan Africa 2024", source_type="research",
        source_url="https://www.gsma.com/mobileeconomy/sub-saharan-africa/",
        confidence="medium",
        original_text="Ethiopia mobile internet penetration ~28% in 2023 (GSMA).",
        notes="Key enabler for digital payments (Sheet C — Indirect Correlation). r=0.91 with ownership.",
    ),
    dict(
        indicator="Bank Branches per 100,000 Adults", indicator_code="ACC_BANK_BRANCHES",
        indicator_direction="higher_better", value_numeric=5.1,
        value_type="rate", unit="per 100k adults", observation_date="2022-12-31",
        pillar="ACCESS", gender="all", location="national",
        source_name="IMF Financial Access Survey 2023", source_type="research",
        source_url="https://data.imf.org/fas",
        confidence="high",
        original_text="Ethiopia: 5.1 commercial bank branches per 100,000 adults (IMF FAS 2022).",
        notes="Very low branch density explains rural reliance on mobile money over formal banking.",
    ),
    dict(
        indicator="ATMs per 100,000 Adults", indicator_code="ACC_ATM_DENSITY",
        indicator_direction="higher_better", value_numeric=4.8,
        value_type="rate", unit="per 100k adults", observation_date="2022-12-31",
        pillar="ACCESS", gender="all", location="national",
        source_name="IMF Financial Access Survey 2023", source_type="research",
        source_url="https://data.imf.org/fas",
        confidence="high",
        original_text="Ethiopia ATM density 4.8 per 100,000 adults (IMF FAS 2022).",
        notes="Contextualises the P2P/ATM crossover milestone (EVT_0006). Sub-Saharan avg is ~8.",
    ),
    dict(
        indicator="Telebirr Registered Users", indicator_code="USG_TELEBIRR_USERS",
        indicator_direction="higher_better", value_numeric=20_000_000,
        value_type="count", unit="users", observation_date="2022-06-30",
        pillar="USAGE", gender="all", location="national",
        source_name="Ethio Telecom Annual Report 2022", source_type="operator",
        source_url="https://www.ethiotelecom.et",
        confidence="medium",
        original_text="Telebirr reached 20 million users by mid-2022.",
        notes="Fills gap between launch (May 2021) and 2025 figure. Needed for growth curve modelling.",
    ),
    dict(
        indicator="Telebirr Registered Users", indicator_code="USG_TELEBIRR_USERS",
        indicator_direction="higher_better", value_numeric=38_000_000,
        value_type="count", unit="users", observation_date="2023-06-30",
        pillar="USAGE", gender="all", location="national",
        source_name="Ethio Telecom Annual Report 2023", source_type="operator",
        source_url="https://www.ethiotelecom.et",
        confidence="medium",
        original_text="Telebirr surpassed 38 million registered users by mid-2023.",
        notes="Enables modelling M-Pesa entry effect (Aug 2023) on Telebirr user growth.",
    ),
    dict(
        indicator="Electricity Access Rate", indicator_code="ELEC_ACCESS",
        indicator_direction="higher_better", value_numeric=45.0,
        value_type="percentage", unit="%", observation_date="2022-12-31",
        pillar="ACCESS", gender="all", location="national",
        source_name="World Bank / ESMAP Tracking SDG7", source_type="research",
        source_url="https://trackingsdg7.esmap.org/country/ethiopia",
        confidence="high",
        original_text="Ethiopia electricity access: ~45% of population in 2022.",
        notes="Electricity is prerequisite for phone charging in rural areas (Sheet C — Indirect Correlate).",
    ),
]


# ── New events ─────────────────────────────────────────────────────────────────

NEW_EVENTS = [
    dict(
        category="regulation",
        indicator="NBE Mobile and Agent Banking Directive (SBB/84/2020)",
        observation_date="2020-07-01",
        source_name="National Bank of Ethiopia", source_type="regulator",
        source_url="https://nbe.gov.et/banking-regulation/directives/",
        confidence="high",
        original_text="NBE issued Directive SBB/84/2020 allowing non-bank entities to offer mobile money services in July 2020.",
        notes="Single most important regulatory event — directly enabled Telebirr launch 10 months later. Missing from original catalog.",
    ),
    dict(
        category="regulation",
        indicator="NBE Payment Instrument Issuer Licensing Framework (2020)",
        observation_date="2020-10-01",
        source_name="National Bank of Ethiopia", source_type="regulator",
        source_url="https://nbe.gov.et/banking-regulation/directives/",
        confidence="high",
        original_text="NBE issued payment instrument issuer licence framework enabling new PSPs in 2020.",
        notes="Underpins EthioPay, Fayda integration and future PSP market entries.",
    ),
    dict(
        category="infrastructure",
        indicator="EthSwitch Full Interoperability Go-Live",
        observation_date="2022-03-01",
        source_name="EthSwitch S.C.", source_type="operator",
        source_url="https://www.ethswitch.com",
        confidence="high",
        original_text="EthSwitch launched full interoperability between banks and mobile money in March 2022.",
        notes="Enables any-to-any transfers. P2P grew 25x from 2022 to 2025 — interoperability is the primary driver.",
    ),
    dict(
        category="infrastructure",
        indicator="Fayda National ID Phase 2 — Biometric Enrolment Scale-Up",
        observation_date="2023-06-01",
        source_name="National ID Program Ethiopia (NIDP)", source_type="regulator",
        source_url="https://id.gov.et",
        confidence="medium",
        original_text="Fayda Phase 2 scaled biometric enrolment to all regions in 2023.",
        notes="Digital ID reduces KYC friction for account opening. India Aadhaar evidence: +35pp over 5 years.",
    ),
    dict(
        category="policy",
        indicator="NBE National Financial Inclusion Strategy II (NFIS-II) 2021-2025",
        observation_date="2021-09-01",
        source_name="National Bank of Ethiopia", source_type="policy",
        source_url="https://nbe.gov.et/financial-inclusion/",
        confidence="high",
        original_text="NFIS-II targets 70% adult financial account ownership by 2025.",
        notes="70% target is for adults (age 15+), not households. Sets benchmark for our forecasting.",
    ),
]


# ── New impact links ────────────────────────────────────────────────────────────

def _build_new_links(main_df: pd.DataFrame, impact_df: pd.DataFrame) -> list:
    """Return list of kwarg dicts for new impact_link rows."""

    def get_evt_id(keyword: str) -> str:
        """Find event record_id by partial indicator match."""
        matches = main_df[
            (main_df["record_type"] == "event") &
            (main_df["indicator"].astype(str).str.contains(keyword, case=False, na=False))
        ]
        if matches.empty:
            logger.warning("No event found matching keyword '%s' — skipping link", keyword)
            return None
        return matches["record_id"].iloc[0]

    new_links = []

    # NBE directive → enabled Telebirr → drives account ownership
    nbe_id = get_evt_id("NBE Mobile and Agent Banking")
    if nbe_id:
        new_links.append(dict(
            parent_id=nbe_id, pillar="ACCESS", related_indicator="ACC_OWNERSHIP",
            relationship_type="enabling", impact_direction="increase",
            impact_magnitude="high", lag_months=10, evidence_basis="empirical",
            comparable_country="Kenya",
            source_name="NBE Directive / Findex trajectory",
            notes="Directive Jul 2020 → Telebirr May 2021 (10-month lag). Root regulatory cause of 2021-2024 mobile money surge.",
        ))

    # EthSwitch interoperability → P2P usage (direct)
    eth_id = get_evt_id("EthSwitch Full Interoperability")
    if eth_id:
        new_links.append(dict(
            parent_id=eth_id, pillar="USAGE", related_indicator="USG_P2P_COUNT",
            relationship_type="direct", impact_direction="increase",
            impact_magnitude="high", lag_months=6, evidence_basis="empirical",
            comparable_country="Tanzania",
            source_name="EthSwitch Annual Reports 2022-2025",
            notes="P2P count grew 25x (49M → 1.28B) 2024-2025. Interoperability removed cross-provider friction.",
        ))

    # EthSwitch interoperability → account ownership (indirect)
    if eth_id:
        new_links.append(dict(
            parent_id=eth_id, pillar="ACCESS", related_indicator="ACC_OWNERSHIP",
            relationship_type="indirect", impact_direction="increase",
            impact_magnitude="medium", lag_months=12, evidence_basis="literature",
            comparable_country="Ghana",
            source_name="World Bank Interoperability Studies 2023",
            notes="Interoperability reduces barriers to opening accounts — World Bank Ghana/Tanzania evidence.",
        ))

    # Fayda Phase 2 → account ownership (enabling, long lag)
    fayda_id = get_evt_id("Fayda National ID Phase 2")
    if fayda_id:
        new_links.append(dict(
            parent_id=fayda_id, pillar="ACCESS", related_indicator="ACC_OWNERSHIP",
            relationship_type="enabling", impact_direction="increase",
            impact_magnitude="medium", lag_months=18, evidence_basis="literature",
            comparable_country="India",
            source_name="World Bank ID4D Studies / Aadhaar evaluation",
            notes="India Aadhaar: digital ID contributed ~35pp inclusion over 5 years. Ethiopia effect will show in 2027 Findex.",
        ))

    return new_links


# ── Main enrichment function ────────────────────────────────────────────────────

def enrich(main_df: pd.DataFrame, impact_df: pd.DataFrame) -> tuple:
    """
    Apply all enrichments and return the updated (main_df, impact_df).

    Parameters
    ----------
    main_df : pd.DataFrame   — output of load_main_dataset()
    impact_df : pd.DataFrame — output of load_impact_links()

    Returns
    -------
    tuple (enriched_main_df, enriched_impact_df)
    """
    original_main_len   = len(main_df)
    original_impact_len = len(impact_df)

    # Add observations
    for obs in NEW_OBSERVATIONS:
        try:
            main_df = _add_obs(main_df, **obs)
        except Exception as exc:
            logger.error("Failed to add observation '%s': %s", obs.get("indicator_code"), exc)

    # Add events
    for evt in NEW_EVENTS:
        try:
            main_df = _add_event(main_df, **evt)
        except Exception as exc:
            logger.error("Failed to add event '%s': %s", evt.get("indicator"), exc)

    # Add impact links
    for link_kwargs in _build_new_links(main_df, impact_df):
        try:
            impact_df = _add_link(impact_df, **link_kwargs)
        except Exception as exc:
            logger.error("Failed to add impact link '%s': %s", link_kwargs.get("related_indicator"), exc)

    # Validate
    issues = _validate_enrichment(main_df, impact_df)
    if issues:
        for issue in issues:
            logger.warning("Validation: %s", issue)
    else:
        logger.info("Enrichment validation passed — no issues found")

    logger.info(
        "Enrichment complete: main %d→%d (+%d), impact %d→%d (+%d)",
        original_main_len, len(main_df), len(main_df) - original_main_len,
        original_impact_len, len(impact_df), len(impact_df) - original_impact_len,
    )
    return main_df, impact_df


def print_enrichment_summary(original_main: pd.DataFrame,
                              enriched_main: pd.DataFrame,
                              enriched_impact: pd.DataFrame) -> None:
    """Print a formatted enrichment summary table to stdout."""
    new_records = enriched_main[~enriched_main["record_id"].isin(original_main["record_id"])]
    new_obs  = new_records[new_records["record_type"] == "observation"]
    new_evts = new_records[new_records["record_type"] == "event"]

    print("\n" + "=" * 65)
    print("  DATA ENRICHMENT SUMMARY")
    print("=" * 65)
    print(f"  Original records  : {len(original_main):>3}")
    print(f"  Enriched records  : {len(enriched_main):>3}  (+{len(enriched_main)-len(original_main)})")
    print(f"    New observations: {len(new_obs):>3}")
    print(f"    New events      : {len(new_evts):>3}")
    print(f"  Impact links      : {len(enriched_impact):>3}  (original 14)")
    print("=" * 65)

    print("\n  NEW OBSERVATIONS:")
    print(f"  {'record_id':<12} {'indicator_code':<25} {'value':>8}  {'date':<12}  {'confidence'}")
    print("  " + "-" * 62)
    for _, r in new_obs.iterrows():
        val = f"{r['value_numeric']:.1f}" if pd.notna(r['value_numeric']) else "—"
        date = str(r['observation_date'])[:10] if pd.notna(r['observation_date']) else "—"
        print(f"  {str(r['record_id']):<12} {str(r['indicator_code']):<25} {val:>8}  {date:<12}  {r['confidence']}")

    print("\n  NEW EVENTS:")
    print(f"  {'record_id':<12} {'category':<18} {'date':<12}  indicator")
    print("  " + "-" * 70)
    for _, r in new_evts.iterrows():
        date = str(r['observation_date'])[:10] if pd.notna(r['observation_date']) else "—"
        label = str(r['indicator'])[:42]
        print(f"  {str(r['record_id']):<12} {str(r['category']):<18} {date:<12}  {label}")
    print("=" * 65 + "\n")


def save_processed(main_df: pd.DataFrame, impact_df: pd.DataFrame) -> None:
    """Save enriched datasets to data/processed/."""
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    main_path   = os.path.join(PROCESSED_DIR, "ethiopia_fi_enriched.csv")
    impact_path = os.path.join(PROCESSED_DIR, "impact_links_enriched.csv")
    main_df.to_csv(main_path,   index=False)
    impact_df.to_csv(impact_path, index=False)
    logger.info("Saved enriched main dataset  → %s", main_path)
    logger.info("Saved enriched impact links  → %s", impact_path)
    print(f"  Saved → {main_path}")
    print(f"  Saved → {impact_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    from src.data_loader import load_all
    data = load_all()

    enriched_main, enriched_impact = enrich(data["main"].copy(), data["impact_links"].copy())
    print_enrichment_summary(data["main"], enriched_main, enriched_impact)
    save_processed(enriched_main, enriched_impact)
