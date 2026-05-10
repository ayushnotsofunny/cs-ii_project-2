# Personal Finance Tracker

A comprehensive personal finance management tool built with Streamlit. This application allows users to effortlessly track their expenses, monitor income streams, set and manage budgets across different categories, and gain insights through interactive dashboards and analytics. Designed for individuals seeking better control over their financial health, it provides an intuitive interface for recording transactions, visualizing spending patterns, and achieving financial goals.

## Features

- Add and manage expenses
- Add and manage income
- View dashboard metrics and charts
- Set budget limits per category
- Create custom categories
- Edit and delete entries
- Filter analytics by date range

## Files

- `src/main.py` — main Streamlit app
- `dist/main.py` — packaged app copy
- `src/data/` — data storage folder
  - `expenses.csv`
  - `income.csv`
  - `budgets.json`
  - `categories.json`
- `requirements.txt` — required Python libraries

## Installation

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run the App

From the project root:

```powershell
streamlit run src/main.py
```

If `streamlit` is not on PATH:

```powershell
python -m streamlit run src/main.py
```

You can also run:

```powershell
streamlit run dist/main.py
```

## How it works

- Data files are stored under `src/data/`
- Default categories and budgets are created if missing
- Expenses and income are saved to CSV
- Budget alerts appear on the dashboard when spending approaches or exceeds limits
- Analytics include expense distribution and daily trend charts

## Dependencies

- `streamlit`
- `pandas`
- `matplotlib`
