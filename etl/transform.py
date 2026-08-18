"""
Transform raw BLS and Census JSON into clean, joinable tables and load
them into a local SQLite database for the dashboard to query.
"""
import os
import json

import pandas as pd
from sqlalchemy import create_engine

try:
    from .fetch_bls import SERIES_IDS, STATE_FIPS
except ImportError:
    from fetch_bls import SERIES_IDS, STATE_FIPS

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
BLS_RAW_PATH = os.path.join(DATA_DIR, "bls_raw.json")
CENSUS_RAW_PATH = os.path.join(DATA_DIR, "census_raw.json")
DB_PATH = os.path.join(DATA_DIR, "labor_market.db")

SERIES_ID_TO_NAME = {
    series_id: series_name for series_name, series_id in SERIES_IDS.items()
}
STATE_SLUG_BY_FIPS = {
    state_fips: state_slug for state_slug, state_fips in STATE_FIPS.items()
}


def transform_bls():
    with open(BLS_RAW_PATH) as f:
        raw = json.load(f)

    rows = []
    for series in raw["Results"]["series"]:
        series_id = series["seriesID"]
        series_name = SERIES_ID_TO_NAME.get(series_id, series_id)
        state_fips = series_id[5:7] if series_id.startswith("LASST") else None
        state_slug = STATE_SLUG_BY_FIPS.get(state_fips)
        state_name = state_slug.replace("_", " ").title() if state_slug else None
        if state_name == "District Of Columbia":
            state_name = "District of Columbia"
        for point in series["data"]:
            # Skip non-monthly periods (e.g., M13 = annual average)
            if not point["period"].startswith("M") or point["period"] == "M13":
                continue
            rows.append({
                "series_id": series_id,
                "series_name": series_name,
                "state_name": state_name,
                "state_fips": state_fips,
                "year": int(point["year"]),
                "month": int(point["period"][1:]),
                "value": pd.to_numeric(point["value"], errors="coerce"),
            })

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(dict(year=df.year, month=df.month, day=1))
    return df.sort_values(["series_name", "date"]).reset_index(drop=True)


def transform_census():
    with open(CENSUS_RAW_PATH) as f:
        records = json.load(f)

    df = pd.DataFrame(records)
    numeric_cols = ["B23025_003E", "B23025_005E", "B15003_022E", "B01001_001E"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.rename(columns={
        "NAME": "state_name",
        "B23025_003E": "labor_force",
        "B23025_005E": "unemployed",
        "B15003_022E": "bachelors_degree",
        "B01001_001E": "total_population",
        "state": "state_fips",
    })
    df["unemployment_rate_pct"] = (df["unemployed"] / df["labor_force"] * 100).round(2)
    df["bachelors_rate_pct"] = (df["bachelors_degree"] / df["total_population"] * 100).round(2)
    return df


def main():
    print("Transforming BLS data...")
    bls_df = transform_bls()

    print("Transforming Census data...")
    census_df = transform_census()

    engine = create_engine(f"sqlite:///{DB_PATH}")
    bls_df.to_sql("bls_timeseries", engine, if_exists="replace", index=False)
    census_df.to_sql("census_state_snapshot", engine, if_exists="replace", index=False)

    print(f"Loaded {len(bls_df)} BLS rows and {len(census_df)} Census rows into {DB_PATH}")


if __name__ == "__main__":
    main()
