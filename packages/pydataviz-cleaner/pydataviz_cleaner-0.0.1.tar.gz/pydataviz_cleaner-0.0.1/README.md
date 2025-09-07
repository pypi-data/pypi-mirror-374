# pydataviz-cleaner

A lightweight Python package to clean messy data for visualization and analysis.

## ✨ Features
- Drop missing values easily
- Remove duplicate rows
- Standardize date formats
- Simple, chainable API for quick data cleaning

## 📦 Installation
```bash
pip install pydataviz-cleaner
```

## 🚀 Usage

```
import pandas as pd
from pydataviz_cleaner.cleaner import DataCleaner

# Example DataFrame
df = pd.DataFrame({
    "name": ["Alice", "Bob", "Bob", None],
    "date": ["2023-01-01", "01/02/2023", "2023-01-02", "invalid"]
})

# Clean the data
cleaner = DataCleaner(df)
cleaned_df = (
    cleaner
    .drop_missing()
    .drop_duplicates()
    .standardize_dates("date")
    .get_df()
)

print(cleaned_df)
```

## 🛠️ Development

- Clone the repo
- Create a virtual environment
- Install dependencies with pip install -e .

## 📜 License

MIT License