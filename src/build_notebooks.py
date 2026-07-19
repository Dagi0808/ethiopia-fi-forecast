"""
build_notebooks.py — generates Task 1 and Task 2 .ipynb files programmatically.
Run: python -m src.build_notebooks
"""
import nbformat as nbf
import os

NB_DIR = os.path.join(os.path.dirname(__file__), "..", "notebooks")


def md(text): return nbf.v4.new_markdown_cell(text)
def code(text): return nbf.v4.new_code_cell(text)


def build_task1():
    nb = nbf.v4.new_notebook()
    nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    cells = []
    cells.append(md("# Task 1 — Data Exploration & Enrichment\n**Ethiopia Financial Inclusion Forecasting | Selam Analytics**\n\nObjective: Understand the starter dataset schema, explore all record types, and enrich the dataset with additional observations, events, and impact links."))
    cells.append(md("## 1. Setup & Imports"))
    cells.append(code("""import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), '..'))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 60)
plt.style.use('seaborn-v0_8-whitegrid')
print("Imports OK")"""))
    cells.append(md("## 2. Load Raw Dataset"))
    cells.append(code("""from src.data_loader import load_all
data = load_all()

main   = data['main']
obs    = data['observations']
events = data['events']
targets= data['targets']
impact = data['impact_links']
ref    = data['reference']

print(f"Main dataset : {main.shape}")
print(f"Observations : {obs.shape}")
print(f"Events       : {events.shape}")
print(f"Targets      : {targets.shape}")
print(f"Impact links : {impact.shape}")
print(f"Reference    : {ref.shape}")"""))
    cells.append(md("## 3. Schema Overview"))
    cells.append(code("""print("=== Columns ===")
print(main.columns.tolist())
print("\\n=== Record types ===")
print(main['record_type'].value_counts())
print("\\n=== Pillars ===")
print(main['pillar'].value_counts(dropna=False))
print("\\n=== Source types ===")
print(main['source_type'].value_counts(dropna=False))
print("\\n=== Confidence levels ===")
print(main['confidence'].value_counts(dropna=False))"""))
    cells.append(md("## 4. Observations — All Indicators"))
    cells.append(code("""obs_summary = (obs.groupby(['indicator_code','indicator','pillar'])
               .agg(records=('record_id','count'),
                    min_date=('observation_date','min'),
                    max_date=('observation_date','max'))
               .reset_index()
               .sort_values('pillar'))
print(obs_summary.to_string(index=False))"""))
    cells.append(md("## 5. Events Catalog"))
    cells.append(code("""print(events[['record_id','category','indicator','observation_date','confidence']]
      .sort_values('observation_date')
      .to_string(index=False))"""))
    cells.append(md("## 6. Impact Links"))
    cells.append(code("""imp_joined = (impact
    .merge(main[['record_id','indicator']], left_on='parent_id', right_on='record_id', suffixes=('','_event'))
    [['record_id','parent_id','indicator_event','pillar','related_indicator',
      'impact_direction','impact_magnitude','lag_months','evidence_basis']]
    .sort_values('parent_id'))
print(imp_joined.to_string(index=False))"""))
    cells.append(md("## 7. Temporal Coverage Heatmap"))
    cells.append(code("""obs2 = obs.copy()
obs2['year'] = obs2['observation_date'].dt.year
coverage = obs2.groupby(['indicator_code','year']).size().unstack(fill_value=0)

fig, ax = plt.subplots(figsize=(12, 7))
sns.heatmap(coverage, cmap='Blues', linewidths=0.5, ax=ax,
            cbar_kws={'label':'Record count'})
ax.set_title("Temporal Coverage — Records per Indicator per Year", fontsize=13, fontweight='bold')
ax.set_xlabel("Year")
ax.set_ylabel("Indicator Code")
plt.tight_layout()
os.makedirs('../reports/figures', exist_ok=True)
plt.savefig('../reports/figures/task1_temporal_coverage.png', dpi=150)
plt.show()
print("Saved: reports/figures/task1_temporal_coverage.png")"""))
    cells.append(md("## 8. Run Enrichment"))
    cells.append(code("""from src.enrich_data import enrich, save_processed
enriched_main, enriched_impact = enrich(data['main'].copy(), data['impact_links'].copy())

print(f"Original records : {len(data['main'])}")
print(f"Enriched records : {len(enriched_main)}")
print(f"  Observations   : {(enriched_main['record_type']=='observation').sum()}")
print(f"  Events         : {(enriched_main['record_type']=='event').sum()}")
print(f"  Targets        : {(enriched_main['record_type']=='target').sum()}")
print(f"Impact links     : {len(enriched_impact)}")

save_processed(enriched_main, enriched_impact)"""))
    cells.append(md("## 9. New Records Summary"))
    cells.append(code("""new_obs = enriched_main[
    (enriched_main['record_type']=='observation') &
    (~enriched_main['record_id'].isin(data['main']['record_id']))
][['record_id','indicator_code','value_numeric','observation_date','pillar','confidence','notes']]
print("=== New Observations ===")
print(new_obs.to_string(index=False))

new_evt = enriched_main[
    (enriched_main['record_type']=='event') &
    (~enriched_main['record_id'].isin(data['main']['record_id']))
][['record_id','category','indicator','observation_date','notes']]
print("\\n=== New Events ===")
print(new_evt.to_string(index=False))"""))
    cells.append(md("## 10. Schema Validation\nConfirm all events have no pillar assigned (key design principle)."))
    cells.append(code("""events_enriched = enriched_main[enriched_main['record_type']=='event']
events_with_pillar = events_enriched['pillar'].dropna()
if len(events_with_pillar) == 0:
    print("✅ All events have pillar = NULL (schema compliant)")
else:
    print(f"⚠️  {len(events_with_pillar)} events have pillar set — review needed")

print("\\nRecord ID uniqueness:", "✅ OK" if not enriched_main['record_id'].dropna().duplicated().any() else "❌ DUPLICATES FOUND")"""))
    nb.cells = cells
    return nb


def build_task2():
    nb = nbf.v4.new_notebook()
    nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    cells = []
    cells.append(md("# Task 2 — Exploratory Data Analysis\n**Ethiopia Financial Inclusion Forecasting | Selam Analytics**\n\nObjective: Analyse patterns in Ethiopia's financial inclusion data, investigate the 2021–2024 stagnation, and document at least 5 key insights with supporting visualisations."))
    cells.append(md("## 0. Setup"))
    cells.append(code("""import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), '..'))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import seaborn as sns

pd.set_option('display.max_columns', None)
plt.style.use('seaborn-v0_8-whitegrid')
COLORS = {'ACCESS':'#1f77b4','USAGE':'#ff7f0e','GENDER':'#2ca02c',
          'AFFORDABILITY':'#d62728','event':'#9467bd'}
os.makedirs('../reports/figures', exist_ok=True)
print("Setup complete")"""))
    cells.append(md("## 1. Load Enriched Dataset"))
    cells.append(code("""from src.data_loader import load_all
from src.enrich_data import enrich

raw = load_all()
main, impact = enrich(raw['main'].copy(), raw['impact_links'].copy())

obs = main[main['record_type']=='observation'].copy()
events = main[main['record_type']=='event'].copy()
targets = main[main['record_type']=='target'].copy()

obs['year'] = obs['observation_date'].dt.year

print(f"Observations: {len(obs)} | Events: {len(events)} | Targets: {len(targets)}")
print(f"\\nPillar breakdown:")
print(obs['pillar'].value_counts(dropna=False))"""))
    nb.cells = cells
    return nb


if __name__ == "__main__":
    nb1 = build_task1()
    path1 = os.path.join(NB_DIR, "01_task1_data_exploration_enrichment.ipynb")
    with open(path1, "w") as f:
        nbf.write(nb1, f)
    print(f"Created: {path1}")
