
# this program appends all sold .csv files into one and cleans them

import pandas as pd
import glob

files = sorted(glob.glob('CRMLSSold*.csv')) # finds sorted csv
print("Files found:", len(files)) # confirms numFiles

sold_date_data = []

for f in files:
    df = pd.read_csv(f)
    print(f, df.shape)
    sold_date_data.append(df)

sold = pd.concat(sold_date_data, ignore_index=True)

# remove duplicate columns like .1
sold = sold.loc[:, ~sold.columns.str.endswith('.1')] # keeps all rows, removes dup columns

print(sold.shape)   # returns 5 rows x 84 columns
print(sold.head())

sold.to_csv("sold_combined.csv", index=False)