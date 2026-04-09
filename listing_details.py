# this .py file preforms analysis on the combined listings.py file made in the previous week

import pandas as pd

listing = pd.read_csv("listing_combined.csv")

# structure validation
print("Shape:", listing.shape)
print("\nColumns:\n", listing.columns)
print("\nHead:\n", listing.head())

# missing value analysis
missing_counts = listing.isnull().sum() # sum of missing counts
missing_pct = (listing.isnull().mean() * 100).round(2) # calculates percentage of missing values
missing_summary = pd.DataFrame({
    "MissingCount": missing_counts, # label
    "MissingPct": missing_pct   # label
}).sort_values("MissingPct", ascending=False)

print("\nMissing Value Summary (Top 20):\n", missing_summary.head(20))
print("\nColumns >90% missing:\n", missing_summary[missing_summary["MissingPct"] > 90])

# 7 num. distribution summary
numeric_cols = ["ClosePrice", "LivingArea", "DaysOnMarket"]
for col in numeric_cols:
    if col in listing.columns:
        data = pd.to_numeric(listing[col], errors="coerce").dropna()

        print(f"\n--- {col} ---")
        print("Min:", data.min())
        print("Max:", data.max())
        print("Mean:", round(data.mean(), 2))
        print("Median:", data.median())

        print("Percentiles:")
        print(data.quantile([0.01, 0.25, 0.5, 0.75, 0.99]))

# days on market distribution
if "DaysOnMarket" in listing.columns:
    dom = pd.to_numeric(listing["DaysOnMarket"], errors="coerce").dropna()
    print("\nDays on Market Summary:\n", dom.describe())

# above vs below price list
if "ClosePrice" in listing.columns and "ListPrice" in listing.columns:
    listing["PriceDiff"] = listing["ClosePrice"] - listing["ListPrice"]

    above = (listing["PriceDiff"] > 0).mean() * 100
    below = (listing["PriceDiff"] < 0).mean() * 100
    equal = (listing["PriceDiff"] == 0).mean() * 100

    print("\nSold Above List (%):", round(above, 2))
    print("Sold Below List (%):", round(below, 2))
    print("Sold At List (%):", round(equal, 2))

# date consistency check
if "ListingDate" in listing.columns and "CloseDate" in listing.columns:
    listing["ListingDate"] = pd.to_datetime(listing["ListingDate"], errors="coerce")
    listing["CloseDate"] = pd.to_datetime(listing["CloseDate"], errors="coerce")

    invalid_dates = listing[listing["CloseDate"] < listing["ListingDate"]]
    print("\nDate Issues (Close < Listing):", len(invalid_dates))

# county median prices
if "CountyOrParish" in listing.columns:
    county_median = listing.groupby("CountyOrParish")["ClosePrice"].median().sort_values(ascending=False)
    print("\nTop Counties by Median Price:\n", county_median.head(10))

# save new file
listing.to_csv("listing_cleaned.csv", index=False)
print("\nSaved: listing_cleaned.csv")