"""
task2_eda.py
------------
Task 2: Exploratory Data Analysis
Generates all figures and prints key insights.
Run: python -m src.task2_eda
Figures saved to: reports/figures/
"""

import os
import sys
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import seaborn as sns

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.data_loader import load_all
from src.enrich_data import enrich

FIGURES = os.path.join(os.path.dirname(__file__), "..", "reports", "figures")
os.makedirs(FIGURES, exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid")
COLORS = {
    "ACCESS": "#1f77b4",
    "USAGE": "#ff7f0e",
    "GENDER": "#2ca02c",
    "event": "#9467bd",
    "target": "#d62728",
}


def load_data():
    raw = load_all()
    main, impact = enrich(raw["main"].copy(), raw["impact_links"].copy())
    obs = main[main["record_type"] == "observation"].copy()
    events = main[main["record_type"] == "event"].copy()
    targets = main[main["record_type"] == "target"].copy()
    obs["year"] = pd.to_datetime(obs["observation_date"]).dt.year
    events["year"] = pd.to_datetime(events["observation_date"]).dt.year
    return obs, events, targets, impact, main


# ── Figure 1: Account Ownership Trajectory 2011–2024 ──────────────────────────

def fig_access_trajectory(obs, events):
    acc = (obs[obs["indicator_code"] == "ACC_OWNERSHIP"].copy()
           .assign(observation_date=lambda d: pd.to_datetime(d["observation_date"], errors="coerce"))
           .sort_values("observation_date")
           .drop_duplicates(subset=["year"])
           .query("year <= 2024"))

    fig, ax = plt.subplots(figsize=(11, 6))

    # main trend line
    ax.plot(acc["year"], acc["value_numeric"], "o-",
            color=COLORS["ACCESS"], linewidth=2.5, markersize=8, zorder=5, label="Account Ownership %")

    # annotate each point
    for _, row in acc.iterrows():
        ax.annotate(f"{row['value_numeric']:.0f}%",
                    xy=(row["year"], row["value_numeric"]),
                    xytext=(0, 12), textcoords="offset points",
                    ha="center", fontsize=10, fontweight="bold", color=COLORS["ACCESS"])

    # growth labels between points
    years = acc["year"].tolist()
    vals = acc["value_numeric"].tolist()
    for i in range(1, len(years)):
        delta = vals[i] - vals[i-1]
        mid_x = (years[i] + years[i-1]) / 2
        mid_y = (vals[i] + vals[i-1]) / 2
        ax.annotate(f"+{delta:.0f}pp", xy=(mid_x, mid_y),
                    xytext=(0, -18), textcoords="offset points",
                    ha="center", fontsize=9, color="grey")

    # NFIS-II 70% target line
    ax.axhline(70, color=COLORS["target"], linestyle="--", linewidth=1.5,
               label="NFIS-II target 70% (2025)")

    # event markers
    key_events = {
        2020: "NBE Directive\n(Jul 2020)",
        2021: "Telebirr\nLaunch (May 2021)",
        2022: "EthSwitch\nInterop (Mar 2022)",
        2023: "M-Pesa\nLaunch (Aug 2023)",
    }
    for yr, label in key_events.items():
        ax.axvline(yr, color=COLORS["event"], linestyle=":", alpha=0.6)
        ax.text(yr + 0.05, 5, label, fontsize=7, color=COLORS["event"],
                rotation=90, va="bottom")

    ax.set_xlim(2010, 2026)
    ax.set_ylim(0, 85)
    ax.set_xlabel("Year", fontsize=11)
    ax.set_ylabel("% of Adults", fontsize=11)
    ax.set_title("Ethiopia Account Ownership Rate 2011–2024\n(World Bank Global Findex)", fontsize=13, fontweight="bold")
    ax.legend(fontsize=9)
    plt.tight_layout()
    path = os.path.join(FIGURES, "fig1_access_trajectory.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


# ── Figure 2: Gender Gap Trend ─────────────────────────────────────────────────

def fig_gender_gap(obs):
    male_codes = {"ACC_OWNERSHIP_M": "Male"}
    female_codes = {"ACC_OWNERSHIP_F": "Female"}

    male = (obs[obs["indicator_code"] == "ACC_OWNERSHIP_M"].copy()
            .assign(observation_date=lambda d: pd.to_datetime(d["observation_date"], errors="coerce"))
            .drop_duplicates("year").sort_values("year"))
    female = (obs[obs["indicator_code"] == "ACC_OWNERSHIP_F"].copy()
              .assign(observation_date=lambda d: pd.to_datetime(d["observation_date"], errors="coerce"))
              .drop_duplicates("year").sort_values("year"))
    gap = (obs[obs["indicator_code"] == "GEN_GAP_ACC"].copy()
           .assign(observation_date=lambda d: pd.to_datetime(d["observation_date"], errors="coerce"))
           .drop_duplicates("year").sort_values("year"))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # left: male vs female ownership
    if not male.empty and not female.empty:
        # align on common years for fill_between
        common = sorted(set(male["year"]) & set(female["year"]))
        m_vals = male.set_index("year").reindex(common)["value_numeric"].astype(float)
        f_vals = female.set_index("year").reindex(common)["value_numeric"].astype(float)
        ax1.plot(male["year"], male["value_numeric"].astype(float), "s-",
                 color="#2166ac", linewidth=2, label="Male")
        ax1.plot(female["year"], female["value_numeric"].astype(float), "o-",
                 color="#d6604d", linewidth=2, label="Female")
        if common:
            ax1.fill_between(common, f_vals.values, m_vals.values,
                             alpha=0.15, color="grey", label="Gap")
        for _, r in male.iterrows():
            ax1.annotate(f"{r['value_numeric']:.0f}%", (r["year"], r["value_numeric"]),
                         textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)
        for _, r in female.iterrows():
            ax1.annotate(f"{r['value_numeric']:.0f}%", (r["year"], r["value_numeric"]),
                         textcoords="offset points", xytext=(0, -14), ha="center", fontsize=9)
        ax1.set_title("Account Ownership by Gender", fontsize=12, fontweight="bold")
        ax1.set_ylabel("% of Adults")
        ax1.set_xlabel("Year")
        ax1.legend()
        ax1.set_ylim(0, 70)

    # right: gender gap pp
    if not gap.empty:
        bars = ax2.bar(gap["year"], gap["value_numeric"],
                       color="#d6604d", alpha=0.75, width=1.5)
        for bar, val in zip(bars, gap["value_numeric"]):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                     f"{val:.0f}pp", ha="center", va="bottom", fontsize=10, fontweight="bold")
        ax2.set_title("Gender Gap in Account Ownership (pp)", fontsize=12, fontweight="bold")
        ax2.set_ylabel("Percentage Points (Male − Female)")
        ax2.set_xlabel("Year")
        ax2.set_ylim(0, 25)
        ax2.axhline(0, color="black", linewidth=0.8)

    plt.suptitle("Financial Inclusion Gender Gap — Ethiopia", fontsize=13, fontweight="bold", y=1.01)
    plt.tight_layout()
    path = os.path.join(FIGURES, "fig2_gender_gap.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


# ── Figure 3: Registered vs Active Gap ────────────────────────────────────────

def fig_registered_vs_active(obs):
    telebirr = (obs[obs["indicator_code"] == "USG_TELEBIRR_USERS"].copy()
                .assign(observation_date=lambda d: pd.to_datetime(d["observation_date"], errors="coerce"))
                .sort_values("observation_date"))
    mpesa = (obs[obs["indicator_code"] == "USG_MPESA_USERS"].copy()
             .assign(observation_date=lambda d: pd.to_datetime(d["observation_date"], errors="coerce"))
             .sort_values("observation_date"))
    active = (obs[obs["indicator_code"] == "USG_MPESA_ACTIVE"].copy()
              .assign(observation_date=lambda d: pd.to_datetime(d["observation_date"], errors="coerce"))
              .sort_values("observation_date"))

    fig, ax = plt.subplots(figsize=(11, 6))

    if not telebirr.empty:
        ax.plot(pd.to_datetime(telebirr["observation_date"]),
                telebirr["value_numeric"] / 1e6, "o-",
                color="#1f77b4", linewidth=2.5, markersize=8, label="Telebirr registered (M)")

    if not mpesa.empty:
        ax.plot(pd.to_datetime(mpesa["observation_date"]),
                mpesa["value_numeric"] / 1e6, "s--",
                color="#ff7f0e", linewidth=2, markersize=7, label="M-Pesa registered (M)")

    if not active.empty:
        ax.scatter(pd.to_datetime(active["observation_date"]),
                   active["value_numeric"] / 1e6, s=120, color="#d62728",
                   zorder=10, label=f"M-Pesa 90-day active (M): {active['value_numeric'].iloc[0]/1e6:.1f}M")

    # annotate Telebirr points
    for _, r in telebirr.iterrows():
        ax.annotate(f"{r['value_numeric']/1e6:.0f}M",
                    (pd.to_datetime(r["observation_date"]), r["value_numeric"]/1e6),
                    textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9)

    ax.set_title("Mobile Money Users: Registered vs Active Gap\nEthiopia 2021–2025", fontsize=13, fontweight="bold")
    ax.set_ylabel("Users (Millions)", fontsize=11)
    ax.set_xlabel("Date", fontsize=11)
    ax.legend(fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}M"))
    plt.tight_layout()
    path = os.path.join(FIGURES, "fig3_registered_vs_active.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


# ── Figure 4: Event Timeline overlaid on Access & Usage ───────────────────────

def fig_event_timeline(obs, events):
    acc = (obs[obs["indicator_code"] == "ACC_OWNERSHIP"].copy()
           .assign(observation_date=lambda d: pd.to_datetime(d["observation_date"], errors="coerce"))
           .drop_duplicates("year").sort_values("year"))
    usg = (obs[obs["indicator_code"] == "USG_DIGITAL_PAYMENT"].copy()
           .assign(observation_date=lambda d: pd.to_datetime(d["observation_date"], errors="coerce"))
           .drop_duplicates("year").sort_values("year"))

    fig, ax = plt.subplots(figsize=(14, 7))

    ax.plot(acc["year"], acc["value_numeric"], "o-",
            color=COLORS["ACCESS"], linewidth=2.5, markersize=9, label="Access (Account Ownership %)", zorder=5)
    if not usg.empty:
        ax.plot(usg["year"], usg["value_numeric"].astype(float), "s--",
                color=COLORS["USAGE"], linewidth=2, markersize=8, label="Usage (Digital Payment %)", zorder=5)

    # event annotations
    evt_colors = {
        "policy": "#d62728", "regulation": "#e377c2",
        "product_launch": "#2ca02c", "infrastructure": "#17becf",
        "market_entry": "#9467bd", "milestone": "#bcbd22",
        "partnership": "#8c564b", "pricing": "#7f7f7f",
    }
    y_positions = [72, 65, 58, 51, 44, 37, 30, 23]
    sorted_evts = (events.copy()
                   .assign(observation_date=lambda d: pd.to_datetime(d["observation_date"], errors="coerce"))
                   .sort_values("observation_date")
                   .reset_index(drop=True))
    for i, (_, evt) in enumerate(sorted_evts.iterrows()):
        yr = pd.to_datetime(evt["observation_date"]).year
        cat = str(evt.get("category", "policy"))
        color = evt_colors.get(cat, "#7f7f7f")
        ypos = y_positions[i % len(y_positions)]
        ax.axvline(yr, color=color, linestyle=":", alpha=0.5, linewidth=1.2)
        label = str(evt["indicator"])[:35]
        ax.annotate(label, xy=(yr, ypos), fontsize=6.5, color=color,
                    rotation=90, va="center", ha="right")

    # build legend for event categories
    patches = [mpatches.Patch(color=c, label=k) for k, c in evt_colors.items() if k in events["category"].values]
    patches += [
        plt.Line2D([0], [0], color=COLORS["ACCESS"], marker="o", linewidth=2, label="Access"),
        plt.Line2D([0], [0], color=COLORS["USAGE"], marker="s", linestyle="--", linewidth=2, label="Usage"),
    ]
    ax.legend(handles=patches, fontsize=7, loc="upper left", ncol=2)
    ax.set_xlim(2010, 2027)
    ax.set_ylim(0, 85)
    ax.set_xlabel("Year", fontsize=11)
    ax.set_ylabel("% of Adults", fontsize=11)
    ax.set_title("Ethiopia Financial Inclusion — Indicator Trends & Key Events", fontsize=13, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(FIGURES, "fig4_event_timeline.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


# ── Figure 5: P2P vs ATM Crossover ────────────────────────────────────────────

def fig_p2p_atm_crossover(obs):
    p2p_count = obs[obs["indicator_code"] == "USG_P2P_COUNT"].copy()
    atm_count = obs[obs["indicator_code"] == "USG_ATM_COUNT"].copy()
    crossover = obs[obs["indicator_code"] == "USG_CROSSOVER"].copy()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # left: transaction counts
    if not p2p_count.empty and not atm_count.empty:
        labels = ["P2P Transactions\n(2024)", "P2P Transactions\n(2025)",
                  "ATM Transactions\n(2024/25)"]
        vals_p2p = p2p_count.sort_values("observation_date")["value_numeric"].tolist()
        vals_atm = atm_count["value_numeric"].tolist()

        x = [0, 1]
        ax1.bar(0, vals_p2p[0] / 1e6 if len(vals_p2p) > 0 else 0,
                color="#1f77b4", alpha=0.7, label=f"P2P 2024: {vals_p2p[0]/1e6:.0f}M" if vals_p2p else "")
        ax1.bar(1, vals_p2p[1] / 1e6 if len(vals_p2p) > 1 else 0,
                color="#1f77b4", alpha=0.9, label=f"P2P 2025: {vals_p2p[1]/1e6:.0f}M" if len(vals_p2p) > 1 else "")
        ax1.bar(2, vals_atm[0] / 1e6 if vals_atm else 0,
                color="#d62728", alpha=0.7, label=f"ATM 2025: {vals_atm[0]/1e6:.0f}M" if vals_atm else "")
        ax1.set_xticks([0, 1, 2])
        ax1.set_xticklabels(["P2P\n(Jul 2024)", "P2P\n(Jul 2025)", "ATM\n(Jul 2025)"])
        ax1.set_title("P2P vs ATM Transaction Counts", fontsize=12, fontweight="bold")
        ax1.set_ylabel("Transactions (Millions)")
        ax1.legend(fontsize=8)

    # right: crossover ratio
    if not crossover.empty:
        ratio = crossover["value_numeric"].iloc[0]
        ax2.pie([ratio, 1], labels=[f"P2P ({ratio:.2f}x ATM)", "ATM (1.0x)"],
                colors=["#1f77b4", "#d62728"], autopct="%1.0f%%", startangle=90,
                explode=[0.05, 0])
        ax2.set_title(f"P2P/ATM Crossover Ratio: {ratio:.2f}x\n(Oct 2024 milestone)", fontsize=12, fontweight="bold")

    plt.suptitle("Digital vs Physical Transaction Milestone — Ethiopia", fontsize=13, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(FIGURES, "fig5_p2p_atm_crossover.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


# ── Figure 6: Infrastructure Enablers ─────────────────────────────────────────

def fig_infrastructure(obs):
    infra_codes = {
        "ACC_4G_COV": "4G Coverage %",
        "ACC_MOBILE_PEN": "Mobile Penetration %",
        "ACC_MOBILE_INTERNET": "Mobile Internet %",
        "ELEC_ACCESS": "Electricity Access %",
    }
    fig, ax = plt.subplots(figsize=(11, 6))
    for code, label in infra_codes.items():
        subset = (obs[obs["indicator_code"] == code].copy()
                  .assign(observation_date=lambda d: pd.to_datetime(d["observation_date"], errors="coerce"))
                  .sort_values("observation_date"))
        if subset.empty:
            continue
        ax.plot(subset["year"], subset["value_numeric"], "o-",
                linewidth=2, markersize=7, label=label)
        for _, r in subset.iterrows():
            ax.annotate(f"{r['value_numeric']:.0f}%",
                        (r["year"], r["value_numeric"]),
                        textcoords="offset points", xytext=(0, 8),
                        ha="center", fontsize=8)

    acc = (obs[obs["indicator_code"] == "ACC_OWNERSHIP"].copy()
           .assign(observation_date=lambda d: pd.to_datetime(d["observation_date"], errors="coerce"))
           .drop_duplicates("year").sort_values("year"))
    ax.plot(acc["year"], acc["value_numeric"], "s--",
            color="black", linewidth=1.5, markersize=6, label="Account Ownership % (ref)", alpha=0.5)

    ax.set_title("Infrastructure Enablers vs Account Ownership — Ethiopia", fontsize=13, fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("% of Population / Adults")
    ax.set_ylim(0, 110)
    ax.legend(fontsize=9)
    plt.tight_layout()
    path = os.path.join(FIGURES, "fig6_infrastructure.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


# ── Figure 7: Data Quality / Confidence Distribution ──────────────────────────

def fig_data_quality(obs):
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))

    # confidence distribution
    conf_counts = obs["confidence"].value_counts()
    axes[0].bar(conf_counts.index, conf_counts.values,
                color=["#2ca02c", "#ff7f0e", "#d62728", "#9467bd"])
    axes[0].set_title("Confidence Level Distribution", fontsize=11, fontweight="bold")
    axes[0].set_ylabel("Record Count")
    for i, (k, v) in enumerate(conf_counts.items()):
        axes[0].text(i, v + 0.2, str(v), ha="center", fontsize=10)

    # source type breakdown
    src_counts = obs["source_type"].value_counts()
    axes[1].barh(src_counts.index, src_counts.values,
                 color=sns.color_palette("Set2", len(src_counts)))
    axes[1].set_title("Source Type Breakdown", fontsize=11, fontweight="bold")
    axes[1].set_xlabel("Record Count")

    # pillar distribution
    pil_counts = obs["pillar"].value_counts(dropna=False)
    axes[2].pie(pil_counts.values, labels=pil_counts.index,
                autopct="%1.0f%%", startangle=90,
                colors=sns.color_palette("Set2", len(pil_counts)))
    axes[2].set_title("Pillar Distribution", fontsize=11, fontweight="bold")

    plt.suptitle("Dataset Quality Assessment", fontsize=13, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(FIGURES, "fig7_data_quality.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


# ── Print Key Insights ─────────────────────────────────────────────────────────

def print_insights(obs):
    print("\n" + "="*70)
    print("KEY INSIGHTS — ETHIOPIA FINANCIAL INCLUSION EDA")
    print("="*70)

    # Insight 1: Growth rates
    acc = (obs[obs["indicator_code"] == "ACC_OWNERSHIP"].copy()
           .assign(observation_date=lambda d: pd.to_datetime(d["observation_date"], errors="coerce"))
           .drop_duplicates("year").sort_values("year"))
    print("\n📌 INSIGHT 1: Uneven growth — spectacular rise then sudden stall")
    years = acc["year"].tolist()
    vals = acc["value_numeric"].tolist()
    for i in range(1, len(years)):
        span = years[i] - years[i-1]
        delta = vals[i] - vals[i-1]
        rate = delta / span
        print(f"   {years[i-1]}→{years[i]}: +{delta:.0f}pp over {span} years ({rate:.1f}pp/yr)")
    print("   → 2021–2024: only +3pp/3yr = 1.0pp/yr despite 65M+ mobile accounts opened")
    print("   → Likely cause: Findex counts 'active' usage, not just registration")

    # Insight 2: Registered vs active
    telebirr = (obs[obs["indicator_code"] == "USG_TELEBIRR_USERS"].copy()
                .assign(observation_date=lambda d: pd.to_datetime(d["observation_date"], errors="coerce"))
                .sort_values("observation_date"))
    acc_mm = (obs[obs["indicator_code"] == "ACC_MM_ACCOUNT"].copy()
              .assign(observation_date=lambda d: pd.to_datetime(d["observation_date"], errors="coerce"))
              .sort_values("observation_date"))
    if not telebirr.empty and not acc_mm.empty:
        latest_tb = telebirr.iloc[-1]["value_numeric"]
        pop_est = 130_000_000
        active_rate = obs[obs["indicator_code"] == "USG_ACTIVE_RATE"]
        ar = active_rate["value_numeric"].iloc[0] / 100 if not active_rate.empty else 0.66
        print(f"\n📌 INSIGHT 2: Massive registered vs active gap")
        print(f"   Telebirr registered (Jun 2025): {latest_tb/1e6:.1f}M")
        print(f"   Estimated active (~{ar*100:.0f}% rate): {latest_tb*ar/1e6:.1f}M")
        print(f"   Adults 15+ in Ethiopia (~{pop_est*0.6/1e6:.0f}M): implies {latest_tb*ar/pop_est/0.6*100:.0f}% coverage")
        print(f"   But Findex says only {acc_mm.iloc[-1]['value_numeric']:.1f}% have MM account")
        print("   → Gap = survey asked about 'past 12 months active use', not registration")

    # Insight 3: P2P crossover
    crossover = obs[obs["indicator_code"] == "USG_CROSSOVER"]
    if not crossover.empty:
        ratio = crossover["value_numeric"].iloc[0]
        print(f"\n📌 INSIGHT 3: P2P transactions now surpass ATM withdrawals ({ratio:.2f}x)")
        print("   → Ethiopia crossed the 'cash-to-digital tipping point' in Oct 2024")
        print("   → Signals genuine behavioral change, not just account registration")
        print("   → Driven by interoperability (EthSwitch 2022) and Telebirr merchant ecosystem")

    # Insight 4: Gender gap
    gap = (obs[obs["indicator_code"] == "GEN_GAP_ACC"].copy()
           .assign(observation_date=lambda d: pd.to_datetime(d["observation_date"], errors="coerce"))
           .sort_values("year"))
    if not gap.empty:
        print("\n📌 INSIGHT 4: Gender gap is stubborn — narrowed only 2pp over 3 years")
        for _, r in gap.iterrows():
            print(f"   {r['year']}: gender gap = {r['value_numeric']:.0f}pp")
        print("   → Mobile phone gender gap (24pp) is the root cause")
        print("   → Female mobile money share only 14% of MM accounts")
        print("   → Targeted interventions needed (agent proximity, ID access, literacy)")

    # Insight 5: Infrastructure correlation
    fayda = (obs[obs["indicator_code"] == "ACC_FAYDA"].copy()
             .assign(observation_date=lambda d: pd.to_datetime(d["observation_date"], errors="coerce"))
             .sort_values("observation_date"))
    if not fayda.empty:
        latest_fayda = fayda.iloc[-1]["value_numeric"]
        print(f"\n📌 INSIGHT 5: Fayda digital ID at {latest_fayda/1e6:.0f}M enrollments — a future inclusion lever")
        print("   → 15M enrolled by May 2025 (target: 90M by 2028)")
        print("   → India Aadhaar evidence: digital ID can add ~35pp inclusion over 5 years")
        print("   → KYC friction is one of Ethiopia's biggest unbanked barriers")
        print("   → If Fayda scales to 60M by 2027, could unlock 5–8pp additional access")

    # Insight 6: NFIS-II target gap
    acc_latest = acc[acc["year"] == 2024]["value_numeric"].iloc[0] if 2024 in acc["year"].values else 49
    target = 70
    print(f"\n📌 INSIGHT 6: NFIS-II target of {target}% by 2025 is out of reach — gap = {target - acc_latest:.0f}pp")
    print(f"   Current: {acc_latest:.0f}% (2024). Need {target - acc_latest:.0f}pp in 1 year.")
    print("   → At best-case 5pp/year, target reached by 2028 under optimistic scenario")
    print("   → Target likely to be revised in NFIS-III or extended timeline")

    print("\n" + "="*70)


def main():
    print("Loading data...")
    obs, events, targets, impact, main = load_data()
    print(f"  {len(obs)} observations | {len(events)} events | {len(targets)} targets")
    print("\nGenerating figures...")
    fig_access_trajectory(obs, events)
    fig_gender_gap(obs)
    fig_registered_vs_active(obs)
    fig_event_timeline(obs, events)
    fig_p2p_atm_crossover(obs)
    fig_infrastructure(obs)
    fig_data_quality(obs)
    print_insights(obs)
    print("\n✅ Task 2 EDA complete. All figures saved to reports/figures/")


if __name__ == "__main__":
    main()
