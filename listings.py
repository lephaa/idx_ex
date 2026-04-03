
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

listings = pd.concat(listing_date_data, ignore_index=True)

# delete duplicate columns, such as livingArea, longitude, etc.
listings = listings.loc[:, ~listings.columns.str.endswith('.1')] # keeps all rows, removes dup columns

print(listings.shape)
print(listings.head())

listings.to_csv("listing_combined.csv", index=False)