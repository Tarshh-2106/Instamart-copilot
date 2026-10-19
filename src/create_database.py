
import os
import sqlite3
import pandas as pd

folder = "data/clean"
db = "data/instamart.db"

tables = {
    "customers": "customers.csv",
    "products": "products.csv",
    "orders": "orders.csv",
    "tickets": "tickets.csv"
}

os.makedirs("data", exist_ok=True)

con = sqlite3.connect(db)

for table, file in tables.items():
    path = os.path.join(folder, file)
    d = pd.read_csv(path)
    d.to_sql(table, con, if_exists="replace", index=False)
    print(f"{table}: {len(d)} rows loaded")

print("\nDatabase tables:")
for row in con.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
):
    print(row[0])

con.close()
print("\nDatabase setup complete.")
