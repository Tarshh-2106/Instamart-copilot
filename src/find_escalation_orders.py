
import sqlite3

con = sqlite3.connect("data/instamart.db")

rows = con.execute(
    """
    SELECT order_id, order_amount, delivery_minutes
    FROM orders
    WHERE status = ?
      AND delivery_minutes > ?
      AND order_amount > ?
    LIMIT 5
    """,
    ("completed", 45, 1000)
).fetchall()

for row in rows:
    print(row)

con.close()
