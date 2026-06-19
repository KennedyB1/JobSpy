"""
Script to find all countries where Novo Nordisk has listed jobs.
Searches across all supported countries on Indeed and LinkedIn.
"""
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jobspy import scrape_jobs
from jobspy.model import Country

# Collect all countries that support Indeed or Glassdoor scraping
# (these are the ones with country_indeed support)
results_by_country = {}

# All countries from the Country enum (excluding internal ones)
all_countries = []
for country in Country:
    if country.name in ("US_CANADA", "WORLDWIDE"):
        continue
    all_countries.append(country)

print(f"Searching for Novo Nordisk jobs across {len(all_countries)} countries...")
print("=" * 70)

countries_with_jobs = []
countries_no_jobs = []
countries_errors = []

for country in all_countries:
    country_str = country.value[0].split(",")[0]  # use first name variant
    try:
        jobs = scrape_jobs(
            site_name=["indeed"],
            search_term="Novo Nordisk",
            results_wanted=5,
            country_indeed=country_str,
            verbose=0,
        )
        if len(jobs) > 0:
            # Get unique locations
            locations = set()
            for _, row in jobs.iterrows():
                loc = row.get("location", "")
                if loc:
                    locations.add(str(loc))
            countries_with_jobs.append((country.name, len(jobs), locations))
            print(f"  ✅ {country.name}: {len(jobs)} jobs found | Locations: {', '.join(list(locations)[:3])}")
        else:
            countries_no_jobs.append(country.name)
            print(f"  ❌ {country.name}: No jobs found")
    except Exception as e:
        countries_errors.append((country.name, str(e)[:80]))
        print(f"  ⚠️  {country.name}: Error - {str(e)[:80]}")

print("\n" + "=" * 70)
print(f"\n📊 SUMMARY")
print(f"Countries with Novo Nordisk jobs: {len(countries_with_jobs)}")
print(f"Countries with no jobs: {len(countries_no_jobs)}")
print(f"Countries with errors: {len(countries_errors)}")

if countries_with_jobs:
    print(f"\n🌍 Countries where Novo Nordisk has listed jobs:")
    for name, count, locations in countries_with_jobs:
        loc_str = ", ".join(list(locations)[:5])
        print(f"   - {name}: {count} job(s) | e.g. {loc_str}")

if countries_errors:
    print(f"\n⚠️  Countries with errors:")
    for name, err in countries_errors:
        print(f"   - {name}: {err}")
