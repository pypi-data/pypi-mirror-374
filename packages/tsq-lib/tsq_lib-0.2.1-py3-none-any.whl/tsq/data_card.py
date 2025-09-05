import pandas as pd
import json
import html
from typing import Dict, Any

def _var_stats(s: pd.Series) -> Dict[str, Any]:
    s_nonan = s.dropna()
    return {
        "n_observations": int(s.shape[0]),
        "n_missing": int(s.isna().sum()),
        "min": None if s_nonan.empty else float(s_nonan.min()),
        "max": None if s_nonan.empty else float(s_nonan.max()),
    }

def generate_data_card(df: pd.DataFrame, dataset_name: str = "Unnamed Dataset") -> Dict[str, Any]:
    """
    Build a finance data card from tidy data: ['timestamp', 'entity', 'variable', 'value'].

    Adds entity-level variable stats under 'entities' -> {entity: {'variables': {var: stats}}}.
    """
    required = {'timestamp', 'entity', 'variable', 'value'}
    if not required.issubset(df.columns):
        raise ValueError(f"Data must contain columns {required}, found {df.columns.tolist()}")

    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    n_obs = len(df)
    n_entities = df['entity'].nunique()
    n_variables = df['variable'].nunique()
    time_min, time_max = df['timestamp'].min(), df['timestamp'].max()
    try:
        freq = pd.infer_freq(df['timestamp'].dropna().sort_values().unique())
    except Exception:
        freq = None

    missing_values = int(df['value'].isna().sum())
    duplicates = int(df.duplicated().sum())
    monotonicity = bool(
        all(
            df.sort_values(['entity', 'timestamp'])
              .groupby('entity', dropna=False)['timestamp']
              .apply(lambda x: x.is_monotonic_increasing or x.is_monotonic_non_decreasing)
        )
    )

    # Variable-level stats (across all entities)
    variables = {}
    for var, g in df.groupby('variable', dropna=False):
        variables[var] = _var_stats(g['value'])

    # Entity-level variable stats
    entities: Dict[str, Any] = {}
    for ent, df_ent in df.groupby('entity', dropna=False):
        ent_vars: Dict[str, Any] = {}
        for var, g in df_ent.groupby('variable', dropna=False):
            ent_vars[var] = _var_stats(g['value'])
        entities[ent] = {
            "n_observations": int(df_ent.shape[0]),
            "n_variables": int(df_ent['variable'].nunique()),
            "time_range": [
                None if pd.isna(df_ent['timestamp'].min()) else str(df_ent['timestamp'].min()),
                None if pd.isna(df_ent['timestamp'].max()) else str(df_ent['timestamp'].max()),
            ],
            "variables": ent_vars
        }

    return {
        "dataset_name": dataset_name,
        "overview": {
            "n_observations": int(n_obs),
            "n_entities": int(n_entities),
            "n_variables": int(n_variables),
            "time_range": [None if pd.isna(time_min) else str(time_min),
                           None if pd.isna(time_max) else str(time_max)],
            "inferred_frequency": freq
        },
        "data_quality": {
            "missing_values": missing_values,
            "duplicates": duplicates,
            "timestamps_monotonic": monotonicity
        },
        "variables": variables,
        "entities": entities  # NEW
    }

def save_data_card_json(df: pd.DataFrame, dataset_name: str, path: str) -> None:
    """
    Generate and save a JSON data card.
    """
    card = generate_data_card(df, dataset_name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(card, f, indent=2)

def save_data_card_html(df: pd.DataFrame, dataset_name: str, path: str) -> None:
    """
    Generate and save an HTML data card, including entity-level variable tables.
    """
    card = generate_data_card(df, dataset_name)

    def b(val): return "✅" if val else "❌"
    title = html.escape(card.get("dataset_name", "Dataset"))
    ov = card["overview"]
    dq = card["data_quality"]
    vars_ = card["variables"]
    ents_ = card["entities"]

    html_content = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{title} — Data Card</title>
<style>
body {{ font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 24px; color:#222; }}
h1 {{ margin-bottom: 0.25rem; }}
h2 {{ margin-top: 2rem; }}
h3 {{ margin-top: 1.25rem; }}
.small {{ color:#666; font-size:0.9rem; }}
.card {{ border:1px solid #e5e7eb; border-radius:12px; padding:16px; margin:12px 0; background:#fafafa; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border-bottom: 1px solid #eee; text-align: left; padding: 8px 6px; }}
th {{ background:#f3f4f6; position: sticky; top: 0; }}
.kv {{ display:grid; grid-template-columns: 240px 1fr; gap:8px 16px; }}
.badge {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; font-size:0.85rem; }}
.entity-block {{ margin-top: 16px; }}
</style></head>
<body>

<h1>Data Card</h1>
<div class="small">{title}</div>

<div class="card">
  <h2>Overview</h2>
  <div class="kv">
    <div>Observations</div><div>{ov['n_observations']}</div>
    <div>Entities</div><div>{ov['n_entities']}</div>
    <div>Variables</div><div>{ov['n_variables']}</div>
    <div>Time range</div><div>{ov['time_range'][0]} — {ov['time_range'][1]}</div>
    <div>Inferred frequency</div><div><span class="badge">{ov['inferred_frequency'] or '—'}</span></div>
  </div>
</div>

<div class="card">
  <h2>Data Quality</h2>
  <div class="kv">
    <div>Missing values</div><div>{dq['missing_values']}</div>
    <div>Duplicates</div><div>{dq['duplicates']}</div>
    <div>Timestamps monotonic per entity</div><div>{b(dq['timestamps_monotonic'])}</div>
  </div>
</div>

<div class="card">
  <h2>Variables (All Entities)</h2>
  <table>
    <thead><tr><th>Variable</th><th>Obs</th><th>Missing</th><th>Min</th><th>Max</th></tr></thead>
    <tbody>
"""
    for var_name, stats in sorted(vars_.items(), key=lambda x: str(x[0])):
        html_content += (
            f"<tr><td>{html.escape(str(var_name))}</td>"
            f"<td>{stats['n_observations']}</td>"
            f"<td>{stats['n_missing']}</td>"
            f"<td>{'' if stats['min'] is None else stats['min']}</td>"
            f"<td>{'' if stats['max'] is None else stats['max']}</td></tr>\n"
        )

    html_content += """    </tbody>
  </table>
</div>

<div class="card">
  <h2>Per-Entity Variable Stats</h2>
"""
    for ent_name, ent_info in sorted(ents_.items(), key=lambda x: str(x[0])):
        ent_title = html.escape(str(ent_name))
        tr0, tr1 = ent_info["time_range"]
        html_content += f"""
  <div class="entity-block">
    <h3>Entity: {ent_title}</h3>
    <div class="kv">
      <div>Entity observations</div><div>{ent_info['n_observations']}</div>
      <div>Entity variables</div><div>{ent_info['n_variables']}</div>
      <div>Entity time range</div><div>{tr0} — {tr1}</div>
    </div>
    <table>
      <thead><tr><th>Variable</th><th>Obs</th><th>Missing</th><th>Min</th><th>Max</th></tr></thead>
      <tbody>
"""
        for var_name, stats in sorted(ent_info["variables"].items(), key=lambda x: str(x[0])):
            html_content += (
                f"<tr><td>{html.escape(str(var_name))}</td>"
                f"<td>{stats['n_observations']}</td>"
                f"<td>{stats['n_missing']}</td>"
                f"<td>{'' if stats['min'] is None else stats['min']}</td>"
                f"<td>{'' if stats['max'] is None else stats['max']}</td></tr>\n"
            )
        html_content += """      </tbody>
    </table>
  </div>
"""
    html_content += """
</div>

<div class="small">Generated by tsq (time series quality)</div>
</body></html>"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(html_content)

def save_data_card_latex(df, dataset_name: str, path: str) -> None:
    card = generate_data_card(df, dataset_name)
    ov = card["overview"]
    dq = card["data_quality"]
    vars_ = card["variables"]
    ents_ = card["entities"]

    latex_content = f"""\\section*{{Data Card: {dataset_name}}}
\\begin{{itemize}}
    \\item Observations: {ov['n_observations']}
    \\item Entities: {ov['n_entities']}
    \\item Variables: {ov['n_variables']}
    \\item Time range: {ov['time_range'][0]} -- {ov['time_range'][1]}
    \\item Inferred frequency: {ov['inferred_frequency'] or '---'}
    \\item Missing values: {dq['missing_values']}
    \\item Duplicates: {dq['duplicates']}
    \\item Timestamps monotonic: {"Yes" if dq['timestamps_monotonic'] else "No"}
\\end{{itemize}}

\\begin{{table}}[h]
\\centering
\\begin{{tabular}}{{lrrrr}}
\\hline
Variable & Obs & Missing & Min & Max \\\\
\\hline
"""
    for var_name, stats in sorted(vars_.items(), key=lambda x: str(x[0])):
        mn = "" if stats["min"] is None else stats["min"]
        mx = "" if stats["max"] is None else stats["max"]
        latex_content += f"{var_name} & {stats['n_observations']} & {stats['n_missing']} & {mn} & {mx} \\\\\n"

    latex_content += """\\hline
\\end{tabular}
\\caption{Variable-level statistics across all entities}
\\end{table}
"""

    # Per-entity tables
    for ent_name, ent_info in sorted(ents_.items(), key=lambda x: str(x[0])):
        tr0, tr1 = ent_info["time_range"]
        latex_content += f"""
\\subsection*{{Entity: {ent_name}}}
\\noindent Observations: {ent_info['n_observations']} \\quad
Variables: {ent_info['n_variables']} \\quad
Time range: {tr0} -- {tr1}

\\begin{{table}}[h]
\\centering
\\begin{{tabular}}{{lrrrr}}
\\hline
Variable & Obs & Missing & Min & Max \\\\
\\hline
"""
        for var_name, stats in sorted(ent_info["variables"].items(), key=lambda x: str(x[0])):
            mn = "" if stats["min"] is None else stats["min"]
            mx = "" if stats["max"] is None else stats["max"]
            latex_content += f"{var_name} & {stats['n_observations']} & {stats['n_missing']} & {mn} & {mx} \\\\\n"

        latex_content += """\\hline
\\end{tabular}
\\caption{Variable-level statistics for entity}
\\end{table}
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(latex_content)
