import pandas as pd
import glob

# load the  data (week 1 output)
files = sorted(glob.glob("CRMLSListing*.csv"))
print("Files found:", len(files))

listing_date_data = []  # empty list

# load data into memory
for f in files:
    df = pd.read_csv(f, low_memory=False)
    print(f, df.shape)
    listing_date_data.append(df)

# combines all monthly files into one dataframe
if listing_date_data:
    rows_before_concat = sum(len(df) for df in listing_date_data)
    print("Rows before concatenation:", rows_before_concat)

    df = pd.concat(listing_date_data, ignore_index=True)
    print("Rows after concatenation:", len(df))
else:   # if no files found, empty dataframe
    df = pd.DataFrame()
    print("Rows before concatenation: 0")
    print("Rows after concatenation: 0")

print(f"Initial shape: {df.shape}") # print shape

# Weeks 2-3: Structuring & EDA
print("\nweeks 2-3")

# unique property types in raw data
if "PropertyType" in df.columns:
    print("\n[Unique Property Types]")
    print(df["PropertyType"].unique())

    # filter to residential
    df = df[df["PropertyType"] == "Residential"].copy()
    print(f"\nFiltered to Residential only. New shape: {df.shape}")

# missing value report (>90% check)
print("\n[Missing Value Report]")
missing_pct = df.isnull().mean()
threshold = 0.90
high_missing_cols = missing_pct[missing_pct > threshold].index.tolist()

print(f"Columns with >90% missing values ({len(high_missing_cols)} total):")
print(high_missing_cols[:5], "...")     # first 5

# drop  sparse columns
core_fields = ['ClosePrice', 'LivingArea', 'BedroomsTotal', 'DaysOnMarket'] # safeguarding core fields
cols_to_drop = [col for col in high_missing_cols if col not in core_fields] # removes non-core sparse fields
df = df.drop(columns=cols_to_drop)
print(f"-> Dropped {len(cols_to_drop)} sparse columns.")

# numeric distribution summary
print("\n[Numeric Distribution Summary]")
cols_of_interest = [c for c in core_fields if c in df.columns]
if cols_of_interest:
    stats = df[cols_of_interest].describe(percentiles=[0.25, 0.5, 0.75, 0.95]).T
    stats = stats.rename(columns={'50%': 'median'})
    print(stats[['min', 'max', 'mean', 'median', '25%', '75%', '95%']])

df.to_csv("filtered_listing_dataset.csv", index=False)

# Weeks 2-3: Mortgage Rate Enrichment
print("\n--- MORTGAGE RATE MERGE ---")

# 1. Fetch FRED Data
print("Fetching FRED Mortgage Data...")
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url, parse_dates=['observation_date'], low_memory=False)
mortgage.columns = ['date', 'rate_30yr_fixed']

# 2. Resample to Monthly
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = mortgage.groupby('year_month')['rate_30yr_fixed'].mean().reset_index()

# 3. Merge and Validate
date_col = 'ListingContractDate'

if date_col in df.columns:
    df['year_month'] = pd.to_datetime(df[date_col], errors='coerce').dt.to_period('M')
    df = df.merge(mortgage_monthly, on='year_month', how='left')

    print(f"Validation Check - Missing mortgage rates after merge: {df['rate_30yr_fixed'].isnull().sum()}")

print("Shape after:", df.shape)

# Weeks 4-5: Cleaning & Flagging
print("\nweeks 4-5")
initial_rows = len(df)

# convert date fields into datetime values for comparison
df["CloseDate"] = pd.to_datetime(df["CloseDate"], errors="coerce")
df["PurchaseContractDate"] = pd.to_datetime(df["PurchaseContractDate"], errors="coerce")
df["ListingContractDate"] = pd.to_datetime(df["ListingContractDate"], errors="coerce")
df["ContractStatusChangeDate"] = pd.to_datetime(df["ContractStatusChangeDate"], errors="coerce")

# ensuring these fields are numeric
df["ClosePrice"] = pd.to_numeric(df["ClosePrice"], errors="coerce")
df["LivingArea"] = pd.to_numeric(df["LivingArea"], errors="coerce")
df["DaysOnMarket"] = pd.to_numeric(df["DaysOnMarket"], errors="coerce")
df["BedroomsTotal"] = pd.to_numeric(df["BedroomsTotal"], errors="coerce")
df["BathroomsTotalInteger"] = pd.to_numeric(df["BathroomsTotalInteger"], errors="coerce")
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

print("\n[Data Type Confirmations]")
print(df[["CloseDate", "ClosePrice", "Latitude"]].dtypes)

# invalid numeric flags
df["invalid_close_price_flag"] = df["ClosePrice"].notna() & (df["ClosePrice"] <= 0)
df["invalid_living_area_flag"] = df["LivingArea"].notna() & (df["LivingArea"] <= 0)
df["invalid_days_on_market_flag"] = df["DaysOnMarket"].notna() & (df["DaysOnMarket"] < 0)
df["invalid_bedrooms_flag"] = df["BedroomsTotal"].notna() & (df["BedroomsTotal"] < 0)
df["invalid_bathrooms_flag"] = df["BathroomsTotalInteger"].notna() & (df["BathroomsTotalInteger"] < 0)

# timeline flags
df["listing_after_close_flag"] = df["ListingContractDate"] > df["CloseDate"]
df["purchase_after_close_flag"] = df["PurchaseContractDate"] > df["CloseDate"]

df["negative_timeline_flag"] = (
    (df["ListingContractDate"] > df["PurchaseContractDate"]) |
    (df["PurchaseContractDate"] > df["CloseDate"])
)

# Geographic flags
df["missing_coords_flag"] = df["Latitude"].isnull() | df["Longitude"].isnull()
df["zero_coords_flag"] = (df["Latitude"] == 0) | (df["Longitude"] == 0)
df["positive_longitude_flag"] = df["Longitude"] > 0

df["implausible_coords_flag"] = (
    ~(
        df["Latitude"].between(32.0, 42.5) &
        df["Longitude"].between(-125.0, -114.0)
    ) &
    df["Latitude"].notnull() &
    df["Longitude"].notnull()
)

# print date flags
print("\nDate flags:")
print("Listing after Close:", df["listing_after_close_flag"].sum())
print("Purchase after Close:", df["purchase_after_close_flag"].sum())
print("Negative Timeline:", df["negative_timeline_flag"].sum())

# print geo flags
print("\nGeo flags:")
print("Missing Coordinates:", df["missing_coords_flag"].sum())
print("Zero Coordinates:", df["zero_coords_flag"].sum())
print("Positive Longitude:", df["positive_longitude_flag"].sum())
print("Implausible Coordinates:", df["implausible_coords_flag"].sum())

# print numeric flags
print("\nInvalid Numeric Flags:")
print("Invalid ClosePrice:", df["invalid_close_price_flag"].sum())
print("Invalid LivingArea:", df["invalid_living_area_flag"].sum())
print("Invalid DaysOnMarket:", df["invalid_days_on_market_flag"].sum())
print("Invalid BedroomsTotal:", df["invalid_bedrooms_flag"].sum())
print("Invalid BathroomsTotalInteger:", df["invalid_bathrooms_flag"].sum())

# prints rows
print("\nRows before:", initial_rows)
print("Rows after:", len(df))

# week 6
# Weeks 6: Feature Engineering and Market Metrics
print("\nweeks 6")

df["LivingArea"] = df["LivingArea"].replace(0, pd.NA)

# ensure date
df["ListingContractDate"] = pd.to_datetime(df["ListingContractDate"], errors="coerce")

# 1. Price Ratio (use ListPrice vs OriginalListPrice if available)
df["price_ratio"] = df["ListPrice"] / df["OriginalListPrice"]

# 2. Price Per Sq Ft
df["price_per_sq_ft"] = df["ListPrice"] / df["LivingArea"]

# 3. Days on Market (already exists)
df["days_on_market"] = df["DaysOnMarket"]

# 4. Year / Month / YrMo (based on listing date)
df["year"] = df["ListingContractDate"].dt.year
df["month"] = df["ListingContractDate"].dt.month
df["yrmo"] = df["ListingContractDate"].dt.strftime("%Y-%m")

# sample output
print("\nSample output:")
print(df[[
    "ListPrice",
    "OriginalListPrice",
    "price_ratio",
    "price_per_sq_ft",
    "days_on_market",
    "yrmo"
]].head(10))

# simple segment summary
print("\nSegment summary (County):")
print(
    df.groupby("CountyOrParish")[["price_ratio", "price_per_sq_ft", "days_on_market"]]
    .mean()
    .head(10)
)

df.to_csv("listing_analysis_ready.csv", index=False)
print("Saved: listing_analysis_ready.csv")