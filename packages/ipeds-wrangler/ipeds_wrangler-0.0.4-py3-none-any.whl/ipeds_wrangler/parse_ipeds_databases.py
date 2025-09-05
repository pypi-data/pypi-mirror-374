import pandas as pd
from access_parser import AccessParser

# identify db file
db_file = "/Users/tereuter/Desktop/sakaar/ipeds_wrangler/ipeds_zip_files/IPEDS_2004-05_Final/IPEDS200405.accdb"
db = AccessParser(db_file)

# display table catalog
print("Tables in the database:")
for table_name in db.catalog.keys():
    print(table_name)

# parse a specific table
table_name = "HD2004"
parsed_table_data = db.parse_table(table_name)

# convert to df
df = pd.DataFrame(parsed_table_data)

# print result
print(df.head())