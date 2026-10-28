import contextlib
import io
import os
import re
import sqlite3
import pandas as pd

with open("sql/queries.sql", encoding="utf-8") as query_file:
    queries = [
        part.strip() for part in
        re.sub(r"(?m)^\s*--.*$", "", query_file.read()).split(";")
        if part.strip()
    ]

report = io.StringIO()
with contextlib.redirect_stdout(report):
    with sqlite3.connect("data/instamart.db") as connection:
        for number, query in enumerate(queries, start=1):
            result = pd.read_sql_query(query, connection)
            print(f"\nQ{number} ({len(result)} rows)")
            print(result.to_string(index=False))

text = report.getvalue()
os.makedirs("outputs", exist_ok=True)
with open("outputs/sql_analysis_results.txt", "w", encoding="utf-8") as output_file:
    output_file.write(text)
print(text, end="")
