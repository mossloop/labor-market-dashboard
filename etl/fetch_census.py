"""
Fetch American Community Survey (ACS) labor force data from the Census API.

Docs: https://www.census.gov/data/developers/data-sets/acs-1year.html

The ACS 1-year estimates give the most current annual snapshot; use the
5-year estimates instead if you need small-geography (county/tract) detail.
"""
import os
import json

import requests
from dotenv import load_dotenv

load_dotenv()

CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")
ACS_YEAR = 2023  # most recent available 1-year ACS at time of writing
ACS_BASE_URL = f"https://api.census.gov/data/{ACS_YEAR}/acs/acs1"

# Example ACS variables:
# B23025_003E = Labor force (population 16+)
# B23025_005E = Unemployed
# B15003_022E = Population 25+ with a bachelor's degree
# B01001_001E = Total population
VARIABLES = {
    "labor_force": "B23025_003E",
    "unemployed": "B23025_005E",
    "bachelors_degree": "B15003_022E",
    "total_population": "B01001_001E",
}

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "census_raw.json")


def fetch_state_data():
    """Fetch labor force / education variables for all U.S. states."""
    var_codes = ",".join(VARIABLES.values())
    params = {
        "get": f"NAME,{var_codes}",
        "for": "state:*",
    }
    if CENSUS_API_KEY:
        params["key"] = CENSUS_API_KEY
    else:
        print("WARNING: No CENSUS_API_KEY found in .env — proceeding "
              "unauthenticated with lower rate limits.")

    response = requests.get(ACS_BASE_URL, params=params)
    response.raise_for_status()
    return response.json()


def main():
    print(f"Fetching ACS {ACS_YEAR} 1-year estimates for all states...")
    raw = fetch_state_data()

    header, *rows = raw
    records = [dict(zip(header, row)) for row in rows]

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(records, f, indent=2)

    print(f"Saved {len(records)} state records to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
