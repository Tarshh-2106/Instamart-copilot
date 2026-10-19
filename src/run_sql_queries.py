
import sqlite3

db = "data/instamart.db"
file = "sql/analysis_queries.sql"

with open(file, "r", encoding="utf-8") as f:
    queries = f.read().split(";")

con = sqlite3.connect(db)

for i, query in enumerate(queries, 1):
    query = query.strip()

    if not query:
        continue

    print(f"\nQUERY {i}")
    print("-" * 50)

    try:
        cur = con.execute(query)
        rows = cur.fetchall()

        if cur.description:
            print([col[0] for col in cur.description])

        for row in rows:
            print(row)

    except sqlite3.Error as e:
        print("SQL ERROR:", e)

con.close()
