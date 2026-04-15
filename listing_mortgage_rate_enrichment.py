import pandas as pd

# Load listing dataset and fetch the mortgage rate data from FRED
listing = pd.read_csv("listing_combined.csv", low_memory=False)

url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url)
mortgage.columns = mortgage.columns.str.strip()

# Rename the FRED columns
mortgage.columns = ["date", "rate_30yr_fixed"]
mortgage["date"] = pd.to_datetime(mortgage["date"])

# Resample weekly rates to monthly averages
mortgage["year_month"] = mortgage["date"].dt.to_period("M")
mortgage_monthly = (
    mortgage.groupby("year_month", as_index=False)["rate_30yr_fixed"]
    .mean()
)

# Create a matching year_month key on the MLS dataset
listing["year_month"] = pd.to_datetime(listing["ListingContractDate"]).dt.to_period("M")

# Merge
listing_with_rates = listing.merge(mortgage_monthly, on="year_month", how="left")

# Validate the merge
print("Missing mortgage rates:", listing_with_rates["rate_30yr_fixed"].isnull().sum())

# Preview
print(listing_with_rates[["ListingContractDate", "year_month", "ListPrice", "rate_30yr_fixed"]].head())

# Save the enriched dataset
listing_with_rates.to_csv("listing_combined_with_rates.csv", index=False)