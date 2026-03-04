# Cricket Analysis (ICC Men's T20 World Cup 2024)

End-to-end cricket analytics project built on ICC Men's T20 World Cup 2024 data, from web scraping to cleaned datasets to role-based player analysis and Power BI dashboards.

## What this project does

1. Scrapes match, batting, bowling, and player metadata from Cricbuzz.
2. Cleans and standardizes raw data in Jupyter notebooks.
3. Builds player-level performance metrics and role-based top-5 rankings.
4. Produces a final Best XI dataset.
5. Visualizes results in Power BI.

## Project Structure

```text
Cricket Analysis/
|-- Web Scrapper/              # Selenium scrapers
|   |-- Match_Summary.py
|   |-- Player_info.py
|   |-- Batting_Summary.py
|   `-- Bowling_Summary.py
|-- Data Cleaning/             # Cleaning and transformation notebooks
|   |-- Match_Summary_Cleaning.ipynb
|   `-- ETL_process.ipynb
|-- CSV/
|   |-- UnCleaned/             # Raw scraped CSVs
|   |-- Cleaned/               # Cleaned, standardized CSVs
|   |-- Measures/              # Feature engineered outputs + final XI
|   `-- data_dictionary.csv
|-- Diagrams/
|   |-- Flow Diagram.pdf
|   |-- data_dictionary.pdf
|   `-- data_dictionary.xlsx
`-- Power Bi Dashboard/
    |-- Cricket Insights.pbix
    `-- Final_reports.pbix
```

## Current Data Snapshot (in repo)

- `CSV/UnCleaned/t20wc.csv`: 55 matches
- `CSV/UnCleaned/player_info.csv`: 304 players
- `CSV/UnCleaned/batting_summary.csv`: 852 batting rows
- `CSV/UnCleaned/bowling_summary.csv`: 595 bowling rows
- `CSV/Cleaned/*.csv`: cleaned versions of the above
- `CSV/Measures/player_performance_summary.csv`: 265 player summaries
- `CSV/Measures/final_best_xi.csv`: final selected XI (11 rows)

## Tech Stack

- Python (data scraping + transformation)
- Selenium (web scraping)
- Pandas (data processing)
- Jupyter Notebook (cleaning + feature engineering)
- Power BI Desktop (dashboard/reporting)

## Prerequisites

1. Python 3.10+ (3.11 recommended)
2. Google Chrome installed
3. Power BI Desktop (for `.pbix` files)
4. Internet connection (required for scraping)

## Setup

Run these commands from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install pandas selenium notebook jupyterlab openpyxl
```

## How to Run

## 1) Quick Start (use existing data)

If you only want analysis/dashboard:

1. Open `Power Bi Dashboard/Cricket Insights.pbix` (or `Final_reports.pbix`) in Power BI Desktop.
2. Click `Refresh`.
3. If Power BI asks for file paths, point it to this repo's `CSV` folders.

## 2) Re-run Web Scraping (raw data generation)

From project root:

```powershell
Set-Location "Web Scrapper"

# Match list
python Match_Summary.py

# Player metadata
python Player_info.py

# Batting and bowling scripts expect T20wc.csv in current folder
Copy-Item t20wc.csv T20wc.csv -Force

python Batting_Summary.py
python Bowling_Summary.py
```

Normalize output names and place into `CSV/UnCleaned`:

```powershell
Rename-Item player_info_t20wc.csv player_info.csv -Force
Rename-Item bowling_summary_all.csv bowling_summary.csv -Force

Copy-Item t20wc.csv "..\CSV\UnCleaned\t20wc.csv" -Force
Copy-Item player_info.csv "..\CSV\UnCleaned\player_info.csv" -Force
Copy-Item batting_summary.csv "..\CSV\UnCleaned\batting_summary.csv" -Force
Copy-Item bowling_summary.csv "..\CSV\UnCleaned\bowling_summary.csv" -Force
```

## 3) Run Cleaning Notebooks

The notebooks currently use local filenames (for example `t20wc.csv`, `player_info.csv`) without folder prefixes.

Recommended approach:

1. Copy raw CSVs from `CSV/UnCleaned` into `Data Cleaning/`.
2. Open Jupyter:

```powershell
Set-Location ".."
jupyter notebook
```

3. Run:
   - `Data Cleaning/Match_Summary_Cleaning.ipynb`
   - `Data Cleaning/ETL_process.ipynb`
4. Save/export outputs into `CSV/Cleaned/`:
   - `t20wc_clean.csv`
   - `player_info_clean.csv`
   - `batting_summary_clean.csv`
   - `bowling_summary_clean.csv`

## 4) Run Measures / Final XI Notebook

`CSV/Measures/Measures.ipynb` reads cleaned files by filename only, so keep required cleaned CSVs in the same working directory (or adjust paths in the first cell).

Expected outputs:

- `player_performance_summary.csv`
- `top5_openers.csv`
- `top5_anchors.csv`
- `top5_middle_order.csv`
- `top5_allrounders.csv`
- `top5_spinners.csv`
- `top5_pacers.csv`
- `final_best_xi.csv`

## Performance Logic Used

Main metrics built in `Measures.ipynb`:

- `strike_rate = (total_runs / balls_faced) * 100`
- `boundary_runs = 4*fours + 6*sixes`
- `boundary_pct = (boundary_runs / total_runs) * 100`
- `bowling_impact = total_wickets*0.6 - economy*0.4` (later version also uses bowling strike rate)
- `batting_impact = total_runs*0.5 + strike_rate*0.3 + boundary_pct*0.2`
- `overall_impact = batting_impact + bowling_impact`

Best XI composition:

- 2 Openers
- 1 Anchor
- 2 Middle Order batters
- 1 All-Rounder
- 2 Spinners
- 3 Pacers

## Important Notes

1. Some notebook cells are exploratory/commented; if you run from scratch, verify cell order and variable initialization before full execution.
2. Cricbuzz page structure can change; Selenium selectors may need updates if scraping breaks.
3. This repo already includes processed CSV outputs, so dashboarding can be done immediately without re-scraping.

## Useful Files

- Data model reference: `Diagrams/data_dictionary.pdf` and `CSV/data_dictionary.csv`
- Pipeline diagram: `Diagrams/Flow Diagram.pdf`
- Final dashboard files: `Power Bi Dashboard/*.pbix`

## Data Source

- Cricbuzz (match pages, scorecards, squads, and player profiles)
