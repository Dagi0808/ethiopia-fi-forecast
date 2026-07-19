"""
build_task1_notebook.py
Generates notebooks/01_task1_data_exploration_enrichment.ipynb
Run: python -m src.build_task1_notebook
"""
import nbformat as nbf, os

NB_DIR = os.path.join(os.path.dirname(__file__), "..", "notebooks")
os.makedirs(NB_DIR, exist_ok=True)

def md(t): return nbf.v4.new_markdown_cell(t)
def code(t): return nbf.v4.new_code_cell(t)

nb = nbf.v4.new_notebook()
nb["metadata"] = {"kernelspec": {"display_name":"Python 3","language":"python","name":"python3"}}
cells = []

cells.append(md("""# Task 1 — Data Exploration & Enrichment
**Project:** Ethiopia Financial Inclusion Forecasting System
**Analyst:** Dag Dagne | Selam Analytics
**Date:** 2026-07-19
**GitHub:** https://github.com/Dagi0808/ethiopia-fi-forecast

---
## Objective
1. Load and understand the unified dataset schema (observations, events, targets, impact_links)
2. Explore all record types, indicators, and temporal coverage
3. Enrich with 15 new observations, 5 new events, and 4 new impact links
4. Validate enrichment against schema rules
"""))

cells.append(md("## 0. Setup"))
cells.append(code("""\
import sys, os, logging
sys.path.insert(0, os.path.join(os.getcwd(), '..'))
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 80)
plt.style.use('seaborn-v0_8-whitegrid')
FIGDIR = '../reports/figures'
os.makedirs(FIGDIR, exist_ok=True)
print("✅ Setup complete")
"""))

cells.append(md("## 1. Load Raw Dataset"))
cells.append(code("""\
from src.data_loader import load_all
data = load_all()

main   = data['main']
obs    = data['observations']
events = data['events']
targets= data['targets']
impact = data['impact_links']
ref    = data['reference']

print(f"Main dataset : {main.shape[0]} rows × {main.shape[1]} columns")
print(f"Observations : {len(obs)}")
print(f"Events       : {len(events)}")
print(f"Targets      : {len(targets)}")
print(f"Impact links : {len(impact)}")
print(f"\\nColumns:")
print(main.columns.tolist())
"""))

cells.append(md("## 2. Schema Understanding — Record Types and Fields"))
cells.append(code("""\
print("=== Record type distribution ===")
print(main['record_type'].value_counts().to_string())

print("\\n=== Pillar distribution (observations + targets) ===")
print(main[main['record_type'].isin(['observation','target'])]['pillar'].value_counts(dropna=False).to_string())

print("\\n=== Source types ===")
print(obs['source_type'].value_counts(dropna=False).to_string())

print("\\n=== Confidence levels ===")
print(obs['confidence'].value_counts(dropna=False).to_string())

print("\\n=== Key design principle: events have NULL pillar ===")
print(f"Events with pillar set: {events['pillar'].dropna().shape[0]} (should be 0)")
"""))

cells.append(md("## 3. All Unique Indicators & Temporal Coverage"))
cells.append(code("""\
obs2 = obs.copy()
obs2['observation_date'] = pd.to_datetime(obs2['observation_date'], errors='coerce')
obs2['year'] = obs2['observation_date'].dt.year

ind_summary = (obs2.groupby(['pillar','indicator_code','indicator'])
               .agg(
                   records = ('record_id','count'),
                   min_year = ('year','min'),
                   max_year = ('year','max'),
                   confidence= ('confidence', lambda x: x.mode()[0] if not x.empty else 'N/A')
               )
               .reset_index()
               .sort_values(['pillar','indicator_code']))
ind_summary
"""))

cells.append(md("### Temporal Coverage Heatmap"))
cells.append(code("""\
coverage = obs2.groupby(['indicator_code','year']).size().unstack(fill_value=0)

fig, ax = plt.subplots(figsize=(13, 8))
sns.heatmap(coverage, cmap='YlOrRd', linewidths=0.5, ax=ax,
            cbar_kws={'label':'Record count'}, annot=True, fmt='d')
ax.set_title('Temporal Coverage — Records per Indicator per Year', fontsize=13, fontweight='bold')
ax.set_xlabel('Year'); ax.set_ylabel('Indicator Code')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'{FIGDIR}/task1_temporal_coverage.png', dpi=150)
plt.show()
print("Saved: reports/figures/task1_temporal_coverage.png")
"""))

cells.append(md("## 4. Events Catalog"))
cells.append(code("""\
events2 = events.copy()
events2['observation_date'] = pd.to_datetime(events2['observation_date'], errors='coerce')
print("=== All Events (sorted by date) ===")
events2[['record_id','category','indicator','observation_date','confidence']].sort_values('observation_date')
"""))

cells.append(md("## 5. Impact Links — Event to Indicator Relationships"))
cells.append(code("""\
imp_joined = (impact
    .merge(main[['record_id','indicator']], left_on='parent_id', right_on='record_id', suffixes=('','_event'))
    [['record_id','parent_id','indicator_event','pillar','related_indicator',
      'impact_direction','impact_magnitude','lag_months','evidence_basis']]
    .sort_values('parent_id'))
print(f"Total impact links: {len(imp_joined)}")
imp_joined
"""))

cells.append(md("## 6. Data Quality Assessment"))
cells.append(code("""\
fig, axes = plt.subplots(1, 3, figsize=(14, 4))

conf = obs['confidence'].value_counts()
axes[0].bar(conf.index, conf.values, color=['#2ca02c','#ff7f0e','#d62728'])
for i,(k,v) in enumerate(conf.items()): axes[0].text(i, v+0.1, str(v), ha='center', fontsize=11, fontweight='bold')
axes[0].set(title='Confidence Levels', ylabel='Count')

src = obs['source_type'].value_counts()
axes[1].barh(src.index, src.values, color=sns.color_palette('Set2', len(src)))
axes[1].set(title='Source Types', xlabel='Count')

pil = obs['pillar'].value_counts(dropna=False)
axes[2].pie(pil.values, labels=pil.index, autopct='%1.0f%%', colors=sns.color_palette('Set2', len(pil)))
axes[2].set_title('Pillars')

plt.suptitle('Raw Dataset Quality (30 observations)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{FIGDIR}/task1_data_quality.png', dpi=150)
plt.show()

print("\\n=== Missing value summary (key columns) ===")
key_cols = ['record_id','record_type','indicator_code','value_numeric','observation_date',
            'pillar','source_name','confidence']
missing = obs[key_cols].isnull().sum()
print(missing[missing > 0].to_string() if missing.any() else "No missing values in key columns ✅")
"""))

cells.append(md("## 7. Run Enrichment & View Summary"))
cells.append(code("""\
from src.enrich_data import enrich, save_processed, print_enrichment_summary

enriched_main, enriched_impact = enrich(data['main'].copy(), data['impact_links'].copy())
print_enrichment_summary(data['main'], enriched_main, enriched_impact)
save_processed(enriched_main, enriched_impact)
"""))

cells.append(md("## 8. New Observations — Detailed View"))
cells.append(code("""\
new_obs = enriched_main[
    (enriched_main['record_type'] == 'observation') &
    (~enriched_main['record_id'].isin(data['main']['record_id']))
].copy()
new_obs['observation_date'] = pd.to_datetime(new_obs['observation_date'], errors='coerce')

new_obs[['record_id','indicator_code','value_numeric','observation_date',
         'pillar','source_name','confidence','notes']].sort_values('observation_date')
"""))

cells.append(md("## 9. New Events — Detailed View"))
cells.append(code("""\
new_evts = enriched_main[
    (enriched_main['record_type'] == 'event') &
    (~enriched_main['record_id'].isin(data['main']['record_id']))
].copy()
new_evts['observation_date'] = pd.to_datetime(new_evts['observation_date'], errors='coerce')

new_evts[['record_id','category','indicator','observation_date','source_name','confidence','notes']].sort_values('observation_date')
"""))

cells.append(md("## 10. New Impact Links — Detailed View"))
cells.append(code("""\
new_links = enriched_impact[
    ~enriched_impact['record_id'].isin(impact['record_id'])
].copy()

linked = new_links.merge(enriched_main[['record_id','indicator']],
                         left_on='parent_id', right_on='record_id',
                         suffixes=('','_event'))
linked[['record_id','parent_id','indicator_event','pillar','related_indicator',
        'impact_direction','impact_magnitude','lag_months','evidence_basis','notes']]
"""))

cells.append(md("## 11. Schema Validation"))
cells.append(code("""\
from src.enrich_data import _validate_enrichment
issues = _validate_enrichment(enriched_main, enriched_impact)

if not issues:
    print("✅ All schema validation checks passed:")
    print("   - No duplicate record_ids")
    print("   - All events have NULL pillar (design principle respected)")
    print("   - All impact_link parent_ids reference existing events")
    print("   - All value_numeric fields are numeric")
else:
    print("⚠️  Validation issues found:")
    for issue in issues:
        print(f"   - {issue}")

print(f"\\nFinal enriched dataset: {len(enriched_main)} records, {len(enriched_impact)} impact links")
"""))

cells.append(md("""## 12. Enrichment Rationale Summary

| Record | Indicator | Why Added |
|--------|-----------|-----------|
| Findex 2011 (ACC_OWNERSHIP 14%) | Missing baseline | Anchors the 13-year trend; without it regression starts at 2014 |
| Male/Female ownership 2014, 2017 | Gender gap series | Enables gender trend 2014→2021→2024; 2017 was the widest gap (16pp) |
| Urban/Rural ownership 2024 | Location disaggregation | 80% of Ethiopians are rural; rural 40% vs urban 68% explains stagnation |
| USG_DIGITAL_PAYMENT 2021 & 2024 | Primary forecast target | Was described in brief but missing as structured records |
| Telebirr users 2022 (20M), 2023 (38M) | Growth curve | Fills 2021→2025 gap; needed to model M-Pesa entry impact |
| IMF FAS: branch density, ATM density | Infrastructure context | Low density (5.1/100k) explains rural mobile-money reliance |
| GSMA mobile internet 28% | Indirect correlate | r=0.91 with account ownership — leading indicator |
| ELEC_ACCESS 45% | Indirect enabler | Electricity is prerequisite for device charging in rural areas |
| NBE Directive SBB/84/2020 | Missing event | Single most important regulatory enabler for Telebirr — was absent |
| EthSwitch interoperability 2022 | Missing event | Direct cause of 25x P2P growth 2022–2025 |
| Fayda Phase 2 2023 | Missing event | Digital ID reduces KYC friction — biggest upcoming inclusion lever |
| 4 new impact links | Event-indicator relationships | NBE→ACCESS, EthSwitch→P2P/ACCESS, Fayda→ACCESS |
"""))

nb.cells = cells
path = os.path.join(NB_DIR, "01_task1_data_exploration_enrichment.ipynb")
with open(path, "w") as f:
    nbf.write(nb, f)
print(f"Created: {path}")
