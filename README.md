# Labor Market Dashboard

An interactive dashboard for exploring U.S. labor market trends — unemployment,
payrolls, wages, and demographic breakdowns — built on public data from the
Bureau of Labor Statistics (BLS) and the U.S. Census Bureau.

## Why this project

Labor market health is a core macro indicator relevant to financial services,
economic research, and workforce planning. This project demonstrates an
end-to-end data pipeline: API ingestion → transformation → storage →
interactive visualization.

## Architecture

```
[BLS API] ──┐
            ├──> [ETL scripts] ──> [SQLite] ──> [Streamlit Dashboard]
[Census API]┘
```

## Setup

1. Clone the repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Get free API keys:
   - BLS: https://data.bls.gov/registrationEngine/ (raises limits from
     25 queries/day, 25 series/query, 10yr range to 500/day, 50 series/query,
     20yr range)
   - Census: https://api.census.gov/data/key_signup.html (optional but
     recommended for higher rate limits)

3. Create a `.env` file in the project root:
   ```
   BLS_API_KEY=your_key_here
   CENSUS_API_KEY=your_key_here
   ```

4. Run the ETL pipeline to populate the database:
   ```bash
   python etl/fetch_bls.py
   python etl/fetch_census.py
   python etl/transform.py
   ```

5. Launch the dashboard:
   ```bash
   streamlit run dashboard/app.py
   ```

## Project structure

```
labor-market-dashboard/
├── etl/
│   ├── fetch_bls.py       # Pull BLS series (unemployment, payrolls, wages)
│   ├── fetch_census.py    # Pull Census ACS demographic data
│   └── transform.py       # Clean, join, and load into SQLite
├── data/
│   └── labor_market.db    # SQLite database (generated)
├── dashboard/
│   └── app.py             # Streamlit dashboard
├── notebooks/
│   └── exploration.ipynb  # Exploratory analysis
├── requirements.txt
└── README.md
```

## Roadmap / stretch goals

- [ ] Add a forecasting model (Prophet/ARIMA) for next-month unemployment rate
- [ ] Deploy to Streamlit Community Cloud
- [ ] Annotate major macro events (recessions, rate hikes) on timelines
- [ ] Add caching layer to respect API rate limits on refresh

## Data sources

- [BLS Public Data API](https://www.bls.gov/developers/) — unemployment,
  nonfarm payrolls, JOLTS, average hourly earnings
- [Census Bureau API](https://www.census.gov/data/developers.html) — American
  Community Survey (ACS) demographic and labor force data
