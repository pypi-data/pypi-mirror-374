# 📊 Time Series Quality (TSQ) Data Card Generator

A Python tool to automatically generate **data cards** (JSON, HTML, LaTeX) from tidy time-series data in the shape: [timestamp, entity, variable, value]

The data card summarizes dataset characteristics, data quality, and per-variable/per-entity statistics.  
Useful for **finance, environmental, health, energy, or any temporal datasets**.

---

## ✨ Features

- Dataset overview (observations, entities, variables, time range, inferred frequency).
- Data quality checks (missing values, duplicates, timestamp monotonicity).
- Variable-level stats (obs, missing, min, max).
- Entity-level breakdown with variable stats.
- Export to:
  - **JSON** (machine-readable)
  - **HTML** (human-readable data card)
  - **LaTeX** (academic reporting)

---

## 📦 Installation

Install directly from PyPI:

```bash
pip install tsq-lib
```


## 🚀 Usage

```python
import pandas as pd
from tsq.data_card import save_data_card_json, save_data_card_html, save_data_card_latex

# Example dataset in tidy format
data = {
    "timestamp": pd.date_range("2025-01-01", periods=5, freq="D").repeat(2),
    "entity": ["AAPL"]*5 + ["MSFT"]*5,
    "variable": ["close"]*10,
    "value": [170, 171, 169, 172, None, 310, 312, 309, 315, 318]
}
df = pd.DataFrame(data)

# Generate JSON, HTML, and LaTeX data cards
save_data_card_json(df, "Example Equity Dataset", "data_card.json")
save_data_card_html(df, "Example Equity Dataset", "data_card.html")
save_data_card_latex(df, "Example Equity Dataset", "data_card.tex")

print("✅ Data card reports saved.")
```

### 📂 Outputs

- **data_card.json** → machine-readable stats  
- **data_card.html** → clean, human-readable data card  
- **data_card.tex** → LaTeX table & section for papers  


## 📖 Examples

This package can be applied across domains. Two example workflows are included:

- **Finance Example**  
  Demonstrates generating a data card for equity price data (e.g. AAPL, MSFT close prices).  
  See: `examples/finance`

- **Air Quality Example**  
  Demonstrates transforming the UCI Air Quality dataset into tidy format and generating a data card with per-variable statistics.  
  See: `examples/air_quality`

## Acknowledgments

Funded by the European Union. Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or European Research Executive Agency (REA). Neither the European Union nor the granting authority can be held responsible for them.

![EU Logo](images/eu_funded_logo.jpg)


## License

MIT — see LICENSE.

