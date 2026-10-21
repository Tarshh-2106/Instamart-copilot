
import sqlite3

db = "data/instamart.db"
file = "sql/queries.sql"

with open(file, "r", encoding="utf-8-sig") as f:
    queries = f.read().split(";")

con = sqlite3.connect(db)

try:
    for i, query in enumerate(queries, 1):
        query = query.strip()

        if not query:
            continue

        print(f"\nQUERY {i}")
        print("-" * 50)

        cur = con.execute(query)

        if cur.description:
            print([col[0] for col in cur.description])
            for row in cur.fetchall():
                print(row)
finally:
    con.close()
