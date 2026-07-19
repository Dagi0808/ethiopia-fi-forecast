"""
enrich_data.py
--------------
Adds new observations, events, and impact_links to the unified dataset
based on external research documented in data_enrichment_log.md.

Run this script to produce:
    data/processed/ethiopia_fi_enriched.csv   — enriched main dataset
    data/processed/impact_links_enriched.csv  — enriched impact links

All new records follow the unified schema defined in reference_codes.xlsx.
"""

import os
import pandas as pd
from src.data_loader import load_all, PROCESSED_DIR

os.makedirs(PROCESSED_DIR, exist_ok=True)


# ── helpers ────────────────────────────────────────────────────────────────────

def _next_rec_id(df: pd.DataFrame, prefix: str) -> str:
    """Generate the next sequential record_id for a given prefix."""
    existing = df["record_id"].dropna().astype(str)
    nums = [
        int(r.replace(prefix, ""))
        for r in existing
        if r.startswith(prefix) and r.replace(prefix, "").isdigit()
    ]
    nxt = max(nums) + 1 if nums else 1
    return f"{prefix}{nxt:04d}"


def _next_imp_id(impact_df: pd.DataFrame) -> str:
    return _next_rec_id(impact_df, "IMP_")


def _new_obs(df, **kwargs) -> pd.Series:
    """
    Build a new observation row with all mandatory fields.
    Caller supplies field values via kwargs; everything else is NaN.
    """
    row = pd.Series({col: None for col in df.columns})
    row["record_type"] = "observation"
    row["collected_by"] = "Dag Dagne"
    row["collection_date"] = "2026-07-19"
    for k, v in kwargs.items():
        row[k] = v
    row["record_id"] = _next_rec_id(df, "REC_")
    return row


def _new_event(df, **kwargs) -> pd.Series:
    row = pd.Series({col: None for col in df.columns})
    row["record_type"] = "event"
    row["pillar"] = None          # events must NOT be pre-assigned a pillar
    row["collected_by"] = "Dag Dagne"
    row["collection_date"] = "2026-07-19"
    for k, v in kwargs.items():
        row[k] = v
    row["record_id"] = _next_rec_id(df, "EVT_")
    return row


def _new_link(impact_df, main_df, **kwargs) -> pd.Series:
    row = pd.Series({col: None for col in impact_df.columns})
    row["record_type"] = "impact_link"
    row["collected_by"] = "Dag Dagne"
    row["collection_date"] = "2026-07-19"
    for k, v in kwargs.items():
        row[k] = v
    row["record_id"] = _next_imp_id(impact_df)
    return row


# ── new observations ────────────────────────────────────────────────────────────

NEW_OBSERVATIONS = [
    # ── Findex 2011 baseline (missing from original dataset) ──────────────────
    dict(
        indicator="Account Ownership Rate",
        indicator_code="ACC_OWNERSHIP",
        indicator_direction="higher_better",
        value_numeric=14.0,
        value_type="percentage",
        unit="%",
        observation_date="2011-12-31",
        pillar="ACCESS",
        gender="all",
        location="national",
        source_name="Global Findex 2011",
        source_type="survey",
        source_url="https://www.worldbank.org/en/publication/globalfindex",
        confidence="high",
        original_text="14% of adults in Ethiopia had an account at a formal financial institution in 2011.",
        notes="2011 Findex baseline — crucial anchor point for 13-year trend analysis.",
    ),
    # ── Female account ownership 2014 (Findex microdata) ─────────────────────
    dict(
        indicator="Account Ownership Rate — Female",
        indicator_code="ACC_OWNERSHIP_F",
        indicator_direction="higher_better",
        value_numeric=16.0,
        value_type="percentage",
        unit="%",
        observation_date="2014-12-31",
        pillar="GENDER",
        gender="female",
        location="national",
        source_name="Global Findex 2014 microdata",
        source_type="survey",
        source_url="https://microdata.worldbank.org/index.php/catalog/2485",
        confidence="high",
        original_text="Female account ownership Ethiopia 2014: ~16% (Findex microdata).",
        notes="Needed to compute gender gap trend from 2014 onwards.",
    ),
    # ── Male account ownership 2014 ───────────────────────────────────────────
    dict(
        indicator="Account Ownership Rate — Male",
        indicator_code="ACC_OWNERSHIP_M",
        indicator_direction="higher_better",
        value_numeric=28.0,
        value_type="percentage",
        unit="%",
        observation_date="2014-12-31",
        pillar="GENDER",
        gender="male",
        location="national",
        source_name="Global Findex 2014 microdata",
        source_type="survey",
        source_url="https://microdata.worldbank.org/index.php/catalog/2485",
        confidence="high",
        original_text="Male account ownership Ethiopia 2014: ~28% (Findex microdata).",
        notes="Needed to compute gender gap trend from 2014 onwards.",
    ),
    # ── Female account ownership 2017 ────────────────────────────────────────
    dict(
        indicator="Account Ownership Rate — Female",
        indicator_code="ACC_OWNERSHIP_F",
        indicator_direction="higher_better",
        value_numeric=27.0,
        value_type="percentage",
        unit="%",
        observation_date="2017-12-31",
        pillar="GENDER",
        gender="female",
        location="national",
        source_name="Global Findex 2017 microdata",
        source_type="survey",
        source_url="https://microdata.worldbank.org/index.php/catalog/3324",
        confidence="high",
        original_text="Female account ownership Ethiopia 2017: ~27% (Findex 2017).",
        notes="Enables gender gap trend 2014–2024.",
    ),
    # ── Male account ownership 2017 ───────────────────────────────────────────
    dict(
        indicator="Account Ownership Rate — Male",
        indicator_code="ACC_OWNERSHIP_M",
        indicator_direction="higher_better",
        value_numeric=43.0,
        value_type="percentage",
        unit="%",
        observation_date="2017-12-31",
        pillar="GENDER",
        gender="male",
        location="national",
        source_name="Global Findex 2017 microdata",
        source_type="survey",
        source_url="https://microdata.worldbank.org/index.php/catalog/3324",
        confidence="high",
        original_text="Male account ownership Ethiopia 2017: ~43% (Findex 2017).",
        notes="Enables gender gap trend 2014–2024.",
    ),
    # ── Urban account ownership 2024 ─────────────────────────────────────────
    dict(
        indicator="Account Ownership Rate — Urban",
        indicator_code="ACC_OWNERSHIP_URB",
        indicator_direction="higher_better",
        value_numeric=68.0,
        value_type="percentage",
        unit="%",
        observation_date="2024-11-29",
        pillar="ACCESS",
        gender="all",
        location="urban",
        source_name="Global Findex 2024",
        source_type="survey",
        source_url="https://www.worldbank.org/en/publication/globalfindex/Report2024",
        confidence="high",
        original_text="Urban account ownership Ethiopia 2024: ~68%.",
        notes="Urban–rural disaggregation needed for inclusion gap analysis.",
    ),
    # ── Rural account ownership 2024 ─────────────────────────────────────────
    dict(
        indicator="Account Ownership Rate — Rural",
        indicator_code="ACC_OWNERSHIP_RUR",
        indicator_direction="higher_better",
        value_numeric=40.0,
        value_type="percentage",
        unit="%",
        observation_date="2024-11-29",
        pillar="ACCESS",
        gender="all",
        location="rural",
        source_name="Global Findex 2024",
        source_type="survey",
        source_url="https://www.worldbank.org/en/publication/globalfindex/Report2024",
        confidence="high",
        original_text="Rural account ownership Ethiopia 2024: ~40%.",
        notes="Rural population is ~80% of Ethiopia — critical for overall inclusion.",
    ),
    # ── Digital payment adoption 2021 (Findex) ───────────────────────────────
    dict(
        indicator="Made or Received Digital Payment",
        indicator_code="USG_DIGITAL_PAYMENT",
        indicator_direction="higher_better",
        value_numeric=18.0,
        value_type="percentage",
        unit="%",
        observation_date="2021-12-31",
        pillar="USAGE",
        gender="all",
        location="national",
        source_name="Global Findex 2021",
        source_type="survey",
        source_url="https://www.worldbank.org/en/publication/globalfindex/Report2021",
        confidence="high",
        original_text="18% of Ethiopian adults made or received a digital payment in 2021.",
        notes="Baseline usage figure before Telebirr's full ramp-up; needed for trend.",
    ),
    # ── Digital payment adoption 2024 (Findex) ───────────────────────────────
    dict(
        indicator="Made or Received Digital Payment",
        indicator_code="USG_DIGITAL_PAYMENT",
        indicator_direction="higher_better",
        value_numeric=35.0,
        value_type="percentage",
        unit="%",
        observation_date="2024-11-29",
        pillar="USAGE",
        gender="all",
        location="national",
        source_name="Global Findex 2024",
        source_type="survey",
        source_url="https://www.worldbank.org/en/publication/globalfindex/Report2024",
        confidence="high",
        original_text="~35% of Ethiopian adults made or received a digital payment in 2024.",
        notes="Core usage target indicator for forecasting.",
    ),
    # ── Mobile internet penetration 2023 (GSMA) ──────────────────────────────
    dict(
        indicator="Mobile Internet Penetration",
        indicator_code="ACC_MOBILE_INTERNET",
        indicator_direction="higher_better",
        value_numeric=28.0,
        value_type="percentage",
        unit="%",
        observation_date="2023-12-31",
        pillar="ACCESS",
        gender="all",
        location="national",
        source_name="GSMA Mobile Economy Sub-Saharan Africa 2024",
        source_type="research",
        source_url="https://www.gsma.com/mobileeconomy/sub-saharan-africa/",
        confidence="medium",
        original_text="Ethiopia mobile internet penetration ~28% in 2023 (GSMA).",
        notes="Key enabler for digital payment adoption; indirect correlate.",
    ),
    # ── Number of bank branches per 100k adults 2022 (IMF FAS) ───────────────
    dict(
        indicator="Bank Branches per 100,000 Adults",
        indicator_code="ACC_BANK_BRANCHES",
        indicator_direction="higher_better",
        value_numeric=5.1,
        value_type="rate",
        unit="per 100k adults",
        observation_date="2022-12-31",
        pillar="ACCESS",
        gender="all",
        location="national",
        source_name="IMF Financial Access Survey 2023",
        source_type="research",
        source_url="https://data.imf.org/fas",
        confidence="high",
        original_text="Ethiopia: 5.1 commercial bank branches per 100,000 adults (IMF FAS 2022).",
        notes="Infrastructure proxy; low branch density explains rural exclusion.",
    ),
    # ── ATM density 2022 (IMF FAS) ────────────────────────────────────────────
    dict(
        indicator="ATMs per 100,000 Adults",
        indicator_code="ACC_ATM_DENSITY",
        indicator_direction="higher_better",
        value_numeric=4.8,
        value_type="rate",
        unit="per 100k adults",
        observation_date="2022-12-31",
        pillar="ACCESS",
        gender="all",
        location="national",
        source_name="IMF Financial Access Survey 2023",
        source_type="research",
        source_url="https://data.imf.org/fas",
        confidence="high",
        original_text="Ethiopia ATM density 4.8 per 100,000 adults (IMF FAS 2022).",
        notes="ATM density gives context to the P2P vs ATM crossover milestone.",
    ),
    # ── Telebirr registered users 2022 (operator report) ─────────────────────
    dict(
        indicator="Telebirr Registered Users",
        indicator_code="USG_TELEBIRR_USERS",
        indicator_direction="higher_better",
        value_numeric=20_000_000,
        value_type="count",
        unit="users",
        observation_date="2022-06-30",
        pillar="USAGE",
        gender="all",
        location="national",
        source_name="Ethio Telecom Annual Report 2022",
        source_type="operator",
        source_url="https://www.ethiotelecom.et",
        confidence="medium",
        original_text="Telebirr reached 20 million users by mid-2022.",
        notes="Intermediate user count between launch (2021) and 2024 figure; needed for growth curve.",
    ),
    # ── Telebirr registered users 2023 ───────────────────────────────────────
    dict(
        indicator="Telebirr Registered Users",
        indicator_code="USG_TELEBIRR_USERS",
        indicator_direction="higher_better",
        value_numeric=38_000_000,
        value_type="count",
        unit="users",
        observation_date="2023-06-30",
        pillar="USAGE",
        gender="all",
        location="national",
        source_name="Ethio Telecom Annual Report 2023",
        source_type="operator",
        source_url="https://www.ethiotelecom.et",
        confidence="medium",
        original_text="Telebirr surpassed 38 million registered users by mid-2023.",
        notes="Fills the 2022–2025 gap in Telebirr growth data.",
    ),
    # ── Electricity access rate 2022 (World Bank) ────────────────────────────
    dict(
        indicator="Electricity Access Rate",
        indicator_code="ELEC_ACCESS",
        indicator_direction="higher_better",
        value_numeric=45.0,
        value_type="percentage",
        unit="%",
        observation_date="2022-12-31",
        pillar="ACCESS",
        gender="all",
        location="national",
        source_name="World Bank Sustainable Energy for All 2023",
        source_type="research",
        source_url="https://trackingsdg7.esmap.org/country/ethiopia",
        confidence="high",
        original_text="Ethiopia electricity access: ~45% of population in 2022.",
        notes="Electricity is a prerequisite for phone charging / digital payments in rural areas.",
    ),
]


# ── new events ─────────────────────────────────────────────────────────────────

NEW_EVENTS = [
    dict(
        category="regulation",
        indicator="NBE Mobile and Agent Banking Directive (SBB/84/2020)",
        observation_date="2020-07-01",
        source_name="National Bank of Ethiopia",
        source_type="regulator",
        source_url="https://nbe.gov.et/banking-regulation/directives/",
        confidence="high",
        original_text="NBE issued Directive SBB/84/2020 allowing non-bank entities to offer mobile money services.",
        notes="This directive opened the door for Ethio Telecom to launch Telebirr. Critical regulatory enabler.",
    ),
    dict(
        category="regulation",
        indicator="NBE Payment Instrument Issuer Licensing (2020)",
        observation_date="2020-10-01",
        source_name="National Bank of Ethiopia",
        source_type="regulator",
        source_url="https://nbe.gov.et/banking-regulation/directives/",
        confidence="high",
        original_text="NBE issued new payment instrument issuer licence framework in 2020.",
        notes="Enabled new PSPs to enter market; underpins Fayda and EthioPay.",
    ),
    dict(
        category="infrastructure",
        indicator="EthSwitch Interoperability Go-Live",
        observation_date="2022-03-01",
        source_name="EthSwitch S.C.",
        source_type="operator",
        source_url="https://www.ethswitch.com",
        confidence="high",
        original_text="EthSwitch launched full interoperability between banks and mobile money in March 2022.",
        notes="Interoperability allows any-to-any transfers, driving P2P usage across all providers.",
    ),
    dict(
        category="policy",
        indicator="National Financial Inclusion Strategy II (NFIS-II) 2021–2025",
        observation_date="2021-09-01",
        source_name="National Bank of Ethiopia",
        source_type="policy",
        source_url="https://nbe.gov.et/financial-inclusion/",
        confidence="high",
        original_text="Ethiopia's NFIS-II targets 70% financial account ownership by 2025.",
        notes="Already in EVT_0009 but adding here to note the 70% target is for adults, not households.",
    ),
    dict(
        category="infrastructure",
        indicator="Fayda National ID Phase 2 — Biometric Enrolment Scale-Up",
        observation_date="2023-06-01",
        source_name="National ID Program Ethiopia (NIDP)",
        source_type="regulator",
        source_url="https://id.gov.et",
        confidence="medium",
        original_text="Fayda Phase 2 scaled biometric enrolment to all regions in 2023.",
        notes="Digital ID enables KYC for mobile money; accelerates financial inclusion in underserved areas.",
    ),
]


# ── new impact links ───────────────────────────────────────────────────────────

def build_new_links(main_df: pd.DataFrame, impact_df: pd.DataFrame) -> list:
    """
    Return a list of new impact_link rows.
    parent_id references must match event record_ids in main_df.
    """
    events = main_df[main_df["record_type"] == "event"].set_index("indicator")
    new_links = []

    def get_evt_id(indicator_name: str) -> str:
        matches = main_df[
            (main_df["record_type"] == "event") &
            (main_df["indicator"].str.contains(indicator_name, case=False, na=False))
        ]
        return matches["record_id"].iloc[0] if not matches.empty else None

    # NBE directive → enabled Telebirr launch → ACCESS
    nbe_id = get_evt_id("NBE Mobile and Agent Banking")
    if nbe_id:
        new_links.append(dict(
            parent_id=nbe_id,
            pillar="ACCESS",
            related_indicator="ACC_OWNERSHIP",
            relationship_type="enabling",
            impact_direction="increase",
            impact_magnitude="high",
            lag_months=10,
            evidence_basis="empirical",
            comparable_country="Kenya",
            source_name="NBE Directive / Findex trajectory",
            notes="Directive enabled Telebirr launch (10 months later), which drove the 2021–2024 ownership rise.",
        ))

    # EthSwitch interoperability → P2P usage increase
    eth_id = get_evt_id("EthSwitch Interoperability")
    if eth_id:
        new_links.append(dict(
            parent_id=eth_id,
            pillar="USAGE",
            related_indicator="USG_P2P_COUNT",
            relationship_type="direct",
            impact_direction="increase",
            impact_magnitude="high",
            lag_months=6,
            evidence_basis="empirical",
            comparable_country="Tanzania",
            source_name="EthSwitch Annual Reports 2022–2025",
            notes="P2P count grew 25x from 2022 to 2025; interoperability enabled cross-provider transfers.",
        ))

    # EthSwitch interoperability → account ownership (indirect, via reduced friction)
    if eth_id:
        new_links.append(dict(
            parent_id=eth_id,
            pillar="ACCESS",
            related_indicator="ACC_OWNERSHIP",
            relationship_type="indirect",
            impact_direction="increase",
            impact_magnitude="medium",
            lag_months=12,
            evidence_basis="literature",
            comparable_country="Ghana",
            source_name="World Bank Interoperability Studies",
            notes="Interoperability lowers barriers, encouraging new users to open accounts.",
        ))

    # Fayda Phase 2 → digital ID reduces KYC friction → account ownership
    fayda_id = get_evt_id("Fayda National ID Phase 2")
    if fayda_id:
        new_links.append(dict(
            parent_id=fayda_id,
            pillar="ACCESS",
            related_indicator="ACC_OWNERSHIP",
            relationship_type="enabling",
            impact_direction="increase",
            impact_magnitude="medium",
            lag_months=18,
            evidence_basis="literature",
            comparable_country="India",
            source_name="World Bank ID4D studies",
            notes="India Aadhaar evidence: digital ID scaled inclusion by ~35pp over 5 years.",
        ))

    return new_links


# ── main enrichment function ───────────────────────────────────────────────────

def enrich(main_df: pd.DataFrame, impact_df: pd.DataFrame) -> tuple:
    """
    Apply all enrichments and return the updated (main_df, impact_df).
    """
    # ── add observations ──────────────────────────────────────────────────────
    for obs in NEW_OBSERVATIONS:
        row = _new_obs(main_df, **obs)
        main_df = pd.concat([main_df, row.to_frame().T], ignore_index=True)

    # ── add events ────────────────────────────────────────────────────────────
    for evt in NEW_EVENTS:
        row = _new_event(main_df, **evt)
        main_df = pd.concat([main_df, row.to_frame().T], ignore_index=True)

    # ── add impact links ──────────────────────────────────────────────────────
    new_links = build_new_links(main_df, impact_df)
    for lnk in new_links:
        row = _new_link(impact_df, main_df, **lnk)
        impact_df = pd.concat([impact_df, row.to_frame().T], ignore_index=True)

    return main_df, impact_df


def save_processed(main_df: pd.DataFrame, impact_df: pd.DataFrame):
    main_path   = os.path.join(PROCESSED_DIR, "ethiopia_fi_enriched.csv")
    impact_path = os.path.join(PROCESSED_DIR, "impact_links_enriched.csv")
    main_df.to_csv(main_path,   index=False)
    impact_df.to_csv(impact_path, index=False)
    print(f"Saved → {main_path}")
    print(f"Saved → {impact_path}")


if __name__ == "__main__":
    data = load_all()
    enriched_main, enriched_impact = enrich(data["main"], data["impact_links"])

    print(f"\nOriginal records : {len(data['main'])}")
    print(f"Enriched records : {len(enriched_main)}")
    print(f"  Observations   : {(enriched_main['record_type']=='observation').sum()}")
    print(f"  Events         : {(enriched_main['record_type']=='event').sum()}")
    print(f"  Targets        : {(enriched_main['record_type']=='target').sum()}")
    print(f"\nOriginal impact links : {len(data['impact_links'])}")
    print(f"Enriched impact links : {len(enriched_impact)}")

    save_processed(enriched_main, enriched_impact)
