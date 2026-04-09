import pandas as pd

sold = pd.read_csv("sold_combined.csv")

# structure validation
print("Shape:", sold.shape)
print("\nColumns:\n", sold.columns)
print("\nHead:\n", sold.head())

# missing value analysis
missing_counts = sold.isnull().sum()  # sum of missing counts
missing_pct = (sold.isnull().mean() * 100).round(2)  # calculates percentage of missing values

missing_summary = pd.DataFrame({
    "MissingCount": missing_counts,
    "MissingPct": missing_pct
}).sort_values("MissingPct", ascending=False)

print("\nMissing Value Summary (Top 20):\n", missing_summary.head(20))
print("\nColumns >90% missing:\n", missing_summary[missing_summary["MissingPct"] > 90])

# numeric distribution summary
numeric_cols = ["ClosePrice", "LivingArea", "DaysOnMarket"]

for col in numeric_cols:
    if col in sold.columns:
        data = pd.to_numeric(sold[col], errors="coerce").dropna()

        print(f"\n--- {col} ---")
        print("Min:", data.min())
        print("Max:", data.max())
        print("Mean:", round(data.mean(), 2))
        print("Median:", data.median())

        print("Percentiles:")
        print(data.quantile([0.01, 0.25, 0.5, 0.75, 0.99]))

# days on market distribution
if "DaysOnMarket" in sold.columns:
    dom = pd.to_numeric(sold["DaysOnMarket"], errors="coerce").dropna()
    print("\nDays on Market Summary:\n", dom.describe())

# above vs below list price
if "ClosePrice" in sold.columns and "ListPrice" in sold.columns:
    sold["PriceDiff"] = sold["ClosePrice"] - sold["ListPrice"]

    above = (sold["PriceDiff"] > 0).mean() * 100
    below = (sold["PriceDiff"] < 0).mean() * 100
    equal = (sold["PriceDiff"] == 0).mean() * 100

    print("\nSold Above List (%):", round(above, 2))
    print("Sold Below List (%):", round(below, 2))
    print("Sold At List (%):", round(equal, 2))

# date consistency check
if "ListingDate" in sold.columns and "CloseDate" in sold.columns:
    sold["ListingDate"] = pd.to_datetime(sold["ListingDate"], errors="coerce")
    sold["CloseDate"] = pd.to_datetime(sold["CloseDate"], errors="coerce")

    invalid_dates = sold[sold["CloseDate"] < sold["ListingDate"]]
    print("\nDate Issues (Close < Listing):", len(invalid_dates))

# county median prices
if "CountyOrParish" in sold.columns and "ClosePrice" in sold.columns:
    county_median = sold.groupby("CountyOrParish")["ClosePrice"].median().sort_values(ascending=False)
    print("\nTop Counties by Median Price:\n", county_median.head(10))

# save new file
sold.to_csv("sold_cleaned.csv", index=False)
print("\nSaved: sold_cleaned.csv")