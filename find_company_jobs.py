"""
==============================================================================
 Global Company Job Finder
==============================================================================

Searches for a company's job postings across LinkedIn, Google, and Indeed
(47+ countries) and returns: Title, Location, Job URL, Date Posted.

HOW TO RUN:

    # Use the default company (Novo Nordisk)
    python find_company_jobs.py

    # Search for a different company
    python find_company_jobs.py "Google"

    # Search with custom time span (e.g. 5 years) and more results
    python find_company_jobs.py "Amazon" --hours 43800 --results 50

    # See all options
    python find_company_jobs.py --help

PARAMETERS (edit at the top of this script):
    COMPANY        - Name of the company to search for
    RESULTS_WANTED - Max results per country per site (default: 20)
    HOURS_OLD      - How far back to search in hours
                       1 year  = 8760
                       2 years = 17520 (default)
                       5 years = 43800
==============================================================================
"""
import sys
import argparse
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jobspy import scrape_jobs
from jobspy.model import Country

# ---- CONFIGURE YOUR SEARCH HERE ----
COMPANY = "Novo Nordisk"       # Change this to any company name
RESULTS_WANTED = 20            # Max results per country per site
HOURS_OLD = 17520              # ~2 years (365 * 24 * 2). 5 years = 43800
# -----------------------------------

# Override via command-line arguments
parser = argparse.ArgumentParser(description="Search for company jobs globally")
parser.add_argument("company", nargs="?", default=COMPANY, help="Company name to search for")
parser.add_argument("--hours", type=int, default=HOURS_OLD, help="Max age in hours (default: 17520 = ~2 years)")
parser.add_argument("--results", type=int, default=RESULTS_WANTED, help="Results per country (default: 20)")
args = parser.parse_args()
COMPANY = args.company
HOURS_OLD = args.hours
RESULTS_WANTED = args.results

# Key countries to search on Indeed (requires country-specific subdomain)
# LinkedIn and Google are searched globally in one pass
KEY_COUNTRIES = [
    "usa", "canada", "uk", "germany", "france", "australia", "india",
    "brazil", "netherlands", "sweden", "denmark", "norway", "finland",
    "switzerland", "austria", "belgium", "ireland", "italy", "spain",
    "poland", "japan", "south korea", "singapore", "mexico", "south africa",
    "argentina", "chile", "colombia", "new zealand", "portugal", "uae",
    "saudi arabia", "egypt", "turkey", "romania", "czech republic", "hungary",
    "malaysia", "thailand", "philippines", "indonesia", "vietnam", "china",
    "russia", "ukraine", "greece", "israel", "pakistan", "bangladesh",
    "nigeria", "kenya", "morocco", "peru", "ecuador",
]

all_jobs = []

# --- Pass 1: Search LinkedIn & Google globally (no country restriction) ---
print("[1/2] Searching LinkedIn & Google globally...")
try:
    jobs_global = scrape_jobs(
        site_name=["linkedin", "google"],
        search_term=COMPANY,
        results_wanted=RESULTS_WANTED,
        hours_old=HOURS_OLD,
        verbose=0,
    )
    if len(jobs_global) > 0:
        all_jobs.append(jobs_global)
        print(f"   Found {len(jobs_global)} jobs from LinkedIn/Google")
except Exception as e:
    print(f"   LinkedIn/Google error: {e}")

# --- Pass 2: Search Indeed across key countries ---
print(f"\n[2/2] Searching Indeed across {len(KEY_COUNTRIES)} countries...")
for i, country in enumerate(KEY_COUNTRIES, 1):
    try:
        jobs = scrape_jobs(
            site_name=["indeed"],
            search_term=COMPANY,
            results_wanted=RESULTS_WANTED,
            country_indeed=country,
            hours_old=HOURS_OLD,
            verbose=0,
        )
        if len(jobs) > 0:
            all_jobs.append(jobs)
            print(f"   [{i}/{len(KEY_COUNTRIES)}] {country}: {len(jobs)} jobs")
    except Exception:
        pass  # skip countries with no results or errors

# --- Combine & display results ---
if not all_jobs:
    print("\nNo jobs found.")
    sys.exit(0)

df = pd.concat(all_jobs, ignore_index=True)

# Deduplicate by job URL if available
if "job_url" in df.columns:
    df = df.drop_duplicates(subset=["job_url"], keep="first")

# Extract only the columns we need
output_cols = []
for col in ["title", "location", "job_url", "date_posted"]:
    if col in df.columns:
        output_cols.append(col)

if not output_cols:
    print("No relevant columns found in results.")
    print(f"Available columns: {list(df.columns)}")
    sys.exit(1)

result = df[output_cols].copy()
result.columns = [c.replace("_", " ").title() for c in result.columns]

print(f"\n{'=' * 70}")
print(f"Total unique jobs found: {len(result)}")
print(f"{'=' * 70}\n")

pd.set_option("display.max_rows", None)
pd.set_option("display.max_colwidth", 80)
pd.set_option("display.width", 200)
print(result.to_string(index=False))

# Save to CSV
safe_name = COMPANY.lower().replace(" ", "_").replace("/", "_")
output_file = f"{safe_name}_jobs.csv"
result.to_csv(output_file, index=False)
print(f"\nResults saved to {output_file}")
