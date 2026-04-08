

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

# Row count before concatenation
rows_before_concat = sum(len(df) for df in sold_date_data)
print("Rows before concatenation:", rows_before_concat)

sold = pd.concat(sold_date_data, ignore_index=True)

# Row count after concatenation
print("Rows after concatenation:", len(sold))

# remove duplicate columns like .1
sold = sold.loc[:, ~sold.columns.str.endswith('.1')] # keeps all rows, removes dup columns

# Row count before Residential filter
print("Rows before Residential filter:", len(sold))

# FILTER: keep only Residential
sold = sold[sold["PropertyType"] == "Residential"]

# Row count after Residential filter
print("Rows after Residential filter:", len(sold))

print(sold.shape)   # 5 rows x 84 columns
print(sold.head())

sold.to_csv("sold_combined.csv", index=False)
