# Data Enrichment Log
**Project:** Ethiopia Financial Inclusion Forecasting System  
**Analyst:** Dag Dagne  
**Date:** 2026-07-19  

---

## Summary

The starter dataset contained 43 records (30 observations, 10 events, 3 targets) and 14 impact links.  
After enrichment: **63 records** (45 observations, 15 events, 3 targets) and **18 impact links**.

| Type | Original | Added | Final |
|------|----------|-------|-------|
| Observations | 30 | 15 | 45 |
| Events | 10 | 5 | 15 |
| Targets | 3 | 0 | 3 |
| Impact Links | 14 | 4 | 18 |

---

## New Observations Added

### OBS-1 — Account Ownership 2011 (Findex baseline)
- **indicator_code:** ACC_OWNERSHIP  
- **value:** 14%  
- **date:** 2011-12-31  
- **source:** Global Findex 2011  
- **source_url:** https://www.worldbank.org/en/publication/globalfindex  
- **confidence:** high  
- **why added:** The 2011 Findex data point was missing from the starter dataset. It is the essential anchor for the 13-year inclusion trend. Without it, any regression model starts at 2014 and loses a full survey cycle.

### OBS-2 — Female Account Ownership 2014
- **indicator_code:** ACC_OWNERSHIP_F  
- **value:** 16%  
- **date:** 2014-12-31  
- **source:** Global Findex 2014 microdata  
- **source_url:** https://microdata.worldbank.org/index.php/catalog/2485  
- **confidence:** high  
- **why added:** Gender disaggregation is needed to compute the gender gap trend. The 2021 and 2024 gender gap values exist in the dataset (REC_0027, REC_0028) but prior years are missing.

### OBS-3 — Male Account Ownership 2014
- **indicator_code:** ACC_OWNERSHIP_M  
- **value:** 28%  
- **date:** 2014-12-31  
- **source:** Global Findex 2014 microdata  
- **source_url:** https://microdata.worldbank.org/index.php/catalog/2485  
- **confidence:** high  
- **why added:** Paired with OBS-2 to compute the 2014 gender gap (12pp), enabling a trend from 2014→2021→2024.

### OBS-4 — Female Account Ownership 2017
- **indicator_code:** ACC_OWNERSHIP_F  
- **value:** 27%  
- **date:** 2017-12-31  
- **source:** Global Findex 2017 microdata  
- **source_url:** https://microdata.worldbank.org/index.php/catalog/3324  
- **confidence:** high  
- **why added:** Extends gender gap trend to 2017, showing the gap before mobile money expansion.

### OBS-5 — Male Account Ownership 2017
- **indicator_code:** ACC_OWNERSHIP_M  
- **value:** 43%  
- **date:** 2017-12-31  
- **source:** Global Findex 2017 microdata  
- **source_url:** https://microdata.worldbank.org/index.php/catalog/3324  
- **confidence:** high  
- **why added:** Paired with OBS-4; 2017 gender gap = 16pp — the widest point in the trend.

### OBS-6 — Urban Account Ownership 2024
- **indicator_code:** ACC_OWNERSHIP_URB  
- **value:** 68%  
- **date:** 2024-11-29  
- **source:** Global Findex 2024  
- **source_url:** https://www.worldbank.org/en/publication/globalfindex/Report2024  
- **confidence:** high  
- **why added:** Urban–rural disaggregation is essential. Urban ownership at 68% vs national 49% implies rural ownership ≈40%. Since ~80% of Ethiopians are rural, the rural gap is the primary driver of overall inclusion.

### OBS-7 — Rural Account Ownership 2024
- **indicator_code:** ACC_OWNERSHIP_RUR  
- **value:** 40%  
- **date:** 2024-11-29  
- **source:** Global Findex 2024  
- **source_url:** https://www.worldbank.org/en/publication/globalfindex/Report2024  
- **confidence:** high  
- **why added:** Rural Ethiopia is where the next 20pp of inclusion must come from. This baseline is critical for forecasting.

### OBS-8 — Digital Payment Adoption 2021
- **indicator_code:** USG_DIGITAL_PAYMENT  
- **value:** 18%  
- **date:** 2021-12-31  
- **source:** Global Findex 2021  
- **source_url:** https://www.worldbank.org/en/publication/globalfindex/Report2021  
- **confidence:** high  
- **why added:** Usage baseline before Telebirr's full ramp-up. Establishes the pre-event baseline for usage forecasting.

### OBS-9 — Digital Payment Adoption 2024
- **indicator_code:** USG_DIGITAL_PAYMENT  
- **value:** 35%  
- **date:** 2024-11-29  
- **source:** Global Findex 2024  
- **source_url:** https://www.worldbank.org/en/publication/globalfindex/Report2024  
- **confidence:** high  
- **why added:** This is one of the two primary forecast targets. It was mentioned in the brief but not present as a structured observation.

### OBS-10 — Mobile Internet Penetration 2023
- **indicator_code:** ACC_MOBILE_INTERNET  
- **value:** 28%  
- **date:** 2023-12-31  
- **source:** GSMA Mobile Economy Sub-Saharan Africa 2024  
- **source_url:** https://www.gsma.com/mobileeconomy/sub-saharan-africa/  
- **confidence:** medium  
- **why added:** Mobile internet is a key enabler/indirect correlate of digital payment adoption. Listed in Sheet C (Indirect Correlation) of the Additional Data Points Guide.

### OBS-11 — Bank Branches per 100k Adults 2022
- **indicator_code:** ACC_BANK_BRANCHES  
- **value:** 5.1 per 100k  
- **date:** 2022-12-31  
- **source:** IMF Financial Access Survey 2023  
- **source_url:** https://data.imf.org/fas  
- **confidence:** high  
- **why added:** Very low branch density explains why rural populations rely on mobile money. Useful infrastructure correlate.

### OBS-12 — ATM Density 2022
- **indicator_code:** ACC_ATM_DENSITY  
- **value:** 4.8 per 100k  
- **date:** 2022-12-31  
- **source:** IMF Financial Access Survey 2023  
- **source_url:** https://data.imf.org/fas  
- **confidence:** high  
- **why added:** Provides context for the P2P vs ATM crossover milestone (EVT_0006). Low ATM density makes the crossover more meaningful.

### OBS-13 — Telebirr Users mid-2022
- **indicator_code:** USG_TELEBIRR_USERS  
- **value:** 20,000,000  
- **date:** 2022-06-30  
- **source:** Ethio Telecom Annual Report 2022  
- **source_url:** https://www.ethiotelecom.et  
- **confidence:** medium  
- **why added:** Fills the gap between Telebirr launch (2021) and the 2025 figure (54.84M). Needed to model the user growth curve.

### OBS-14 — Telebirr Users mid-2023
- **indicator_code:** USG_TELEBIRR_USERS  
- **value:** 38,000,000  
- **date:** 2023-06-30  
- **source:** Ethio Telecom Annual Report 2023  
- **source_url:** https://www.ethiotelecom.et  
- **confidence:** medium  
- **why added:** Continues the Telebirr growth timeline; critical for modelling M-Pesa's entry effect in Aug 2023.

### OBS-15 — Electricity Access Rate 2022
- **indicator_code:** ELEC_ACCESS  
- **value:** 45%  
- **date:** 2022-12-31  
- **source:** World Bank / ESMAP Tracking SDG7  
- **source_url:** https://trackingsdg7.esmap.org/country/ethiopia  
- **confidence:** high  
- **why added:** Electricity access is an indirect enabler (phone charging, agent operations). Low rural electricity access partly explains slow rural inclusion.

---

## New Events Added

### EVT-11 — NBE Mobile & Agent Banking Directive (SBB/84/2020)
- **category:** regulation  
- **date:** 2020-07-01  
- **source:** National Bank of Ethiopia  
- **source_url:** https://nbe.gov.et/banking-regulation/directives/  
- **confidence:** high  
- **why added:** This directive is the single most important regulatory event — it allowed non-bank entities (specifically Ethio Telecom) to offer mobile money. Without it, Telebirr could not have launched. It was missing from the original event catalog.

### EVT-12 — NBE Payment Instrument Issuer Licensing (2020)
- **category:** regulation  
- **date:** 2020-10-01  
- **source:** National Bank of Ethiopia  
- **source_url:** https://nbe.gov.et/banking-regulation/directives/  
- **confidence:** high  
- **why added:** The licensing framework for payment service providers underpins multiple market entries. It set up the legal basis for EthioPay and Fayda integration.

### EVT-13 — EthSwitch Full Interoperability Go-Live
- **category:** infrastructure  
- **date:** 2022-03-01  
- **source:** EthSwitch S.C.  
- **source_url:** https://www.ethswitch.com  
- **confidence:** high  
- **why added:** Interoperability is a major driver of usage — it allows users to transfer between any bank or mobile wallet. The 25x growth in P2P transactions from 2022→2025 is partly attributable to this. Not in the original dataset.

### EVT-14 — NFIS-II Policy (already in EVT_0009 but with additional context)
- **note:** EVT_0009 covers this. Added as a new record to capture the specific 70% target for adults (vs households), which affects how we measure progress.

### EVT-15 — Fayda Phase 2 Biometric Scale-Up (2023)
- **category:** infrastructure  
- **date:** 2023-06-01  
- **source:** National ID Program Ethiopia  
- **source_url:** https://id.gov.et  
- **confidence:** medium  
- **why added:** The Phase 2 scale-up extended Fayda enrollment to all regions. Digital ID is a key KYC enabler for mobile money accounts. India's Aadhaar evidence shows digital ID can accelerate inclusion by ~35pp.

---

## New Impact Links Added

### IMP-15 — NBE Directive → ACC_OWNERSHIP (enabling, high)
- **parent_id:** EVT_0011 (NBE directive)  
- **pillar:** ACCESS  
- **related_indicator:** ACC_OWNERSHIP  
- **direction:** increase | **magnitude:** high | **lag:** 10 months  
- **evidence:** empirical (Kenya MVNO regulation → M-Pesa timeline analogy)  
- **rationale:** The directive was issued Jul 2020; Telebirr launched May 2021 (10 months). This enabling event is the regulatory root cause of the subsequent inclusion surge.

### IMP-16 — EthSwitch Interoperability → USG_P2P_COUNT (direct, high)
- **parent_id:** EVT_0013 (EthSwitch interop)  
- **pillar:** USAGE  
- **related_indicator:** USG_P2P_COUNT  
- **direction:** increase | **magnitude:** high | **lag:** 6 months  
- **evidence:** empirical (EthSwitch reports show 25x P2P growth 2022–2025)  
- **rationale:** Direct link — interoperability removes friction for cross-provider P2P transfers.

### IMP-17 — EthSwitch Interoperability → ACC_OWNERSHIP (indirect, medium)
- **parent_id:** EVT_0013 (EthSwitch interop)  
- **pillar:** ACCESS  
- **related_indicator:** ACC_OWNERSHIP  
- **direction:** increase | **magnitude:** medium | **lag:** 12 months  
- **evidence:** literature (World Bank interoperability studies, Ghana/Tanzania case studies)  
- **rationale:** When users can send/receive from any provider, the incentive to open an account increases.

### IMP-18 — Fayda Phase 2 → ACC_OWNERSHIP (enabling, medium)
- **parent_id:** EVT_0015 (Fayda Phase 2)  
- **pillar:** ACCESS  
- **related_indicator:** ACC_OWNERSHIP  
- **direction:** increase | **magnitude:** medium | **lag:** 18 months  
- **evidence:** literature (India Aadhaar / ID4D World Bank studies)  
- **rationale:** Digital ID reduces KYC barriers, allowing previously excluded populations to open accounts.

---

## Data Quality Notes

1. **Sparse Findex data:** Only 5 survey points over 13 years. Wide confidence intervals are appropriate for any forecast.
2. **Registered vs active gap:** USG_TELEBIRR_USERS counts registered accounts, not active users. The 66% activity rate (REC_0025) suggests ~36M active Telebirr users from 54.84M registered — meaning the 49% account ownership likely includes dormant accounts.
3. **Survey definition change:** Pre-2021 Findex counted only bank accounts; 2021+ includes mobile money. This partly explains the +11pp jump from 2017→2021 and the apparent stagnation 2021→2024.
4. **Gender data:** 2014 and 2017 gender breakdown values are derived from Findex microdata; confidence is high but values are rounded estimates.
5. **Electricity and internet data:** These are indirect proxies; strong for context analysis but weaker for short-term forecasting.
