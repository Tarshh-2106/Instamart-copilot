import os
import sqlite3
import pandas as pd

DB = "data/instamart.db"
TABLES = ("customers", "products", "orders")

os.makedirs("data", exist_ok=True)
with sqlite3.connect(DB) as connection:
    connection.execute("DROP TABLE IF EXISTS tickets")
    for table in TABLES:
        frame = pd.read_csv(f"data/clean/{table}.csv")
        if table == "orders":
            frame["order_ts"] = pd.to_datetime(frame["order_ts"]).dt.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        frame.to_sql(table, connection, if_exists="replace", index=False)
        print(f"{table}: {len(frame)} rows loaded")

print("Database setup complete.")
