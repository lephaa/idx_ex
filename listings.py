
# this program appends all listing .csv files into one and cleans them

import pandas as pd
import glob

files = sorted(glob.glob('CRMLSListing*.csv'))  # finds sorted csv
print("Files found:", len(files))   # confirms numFiles

listing_date_data = []

for f in files:
    df = pd.read_csv(f)
    print(f, df.shape)
    listing_date_data.append(df)

# Row count before concatenation
rows_before_concat = sum(len(df) for df in listing_date_data)
print("Rows before concatenation:", rows_before_concat)

listings = pd.concat(listing_date_data, ignore_index=True)

# Row count after concatenation
print("Rows after concatenation:", len(listings))

# delete duplicate columns, such as livingArea, longitude, etc.
listings = listings.loc[:, ~listings.columns.str.endswith('.1')]

# Row count before Residential filter
print("Rows before Residential filter:", len(listings))

# FILTER: keep only Residential
listings = listings[listings["PropertyType"] == "Residential"]

# Row count after Residential filter
print("Rows after Residential filter:", len(listings))

print(listings.shape)
print(listings.head())

listings.to_csv("listing_combined.csv", index=False)
