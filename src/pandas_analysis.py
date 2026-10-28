import os
import sqlite3
import pandas as pd

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = os.path.join(base, "data", "clean")
out = os.path.join(base, "outputs")

os.makedirs(out, exist_ok=True)

customers = pd.read_csv(os.path.join(data, "customers.csv"))
orders = pd.read_csv(os.path.join(data, "orders.csv"))
products = pd.read_csv(os.path.join(data, "products.csv"))
tickets = pd.read_csv(
    os.path.join(data, "tickets.csv"), keep_default_na=False
)

lines = []

def add(title, value):
    lines.append(f"\n{title}\n")
    if isinstance(value, pd.DataFrame):
        lines.append(value.to_string())
    elif isinstance(value, pd.Series):
        lines.append(value.to_string())
    else:
        lines.append(str(value))
    lines.append("\n")

add("DATASET SHAPES", {
    "customers": customers.shape,
    "orders": orders.shape,
    "products": products.shape,
    "tickets": tickets.shape
})

raw_tables = {
    name: pd.read_csv(
        os.path.join(base, "data", "raw", f"{name}.csv"),
        keep_default_na=False if name == "tickets" else True
    )
    for name in ("customers", "orders", "tickets")
}
for name, frame in raw_tables.items():
    missing = frame.replace("", pd.NA).isna().sum()
    add(f"RAW {name.upper()} SHAPE", frame.shape)
    add(f"RAW {name.upper()} DTYPES", frame.dtypes.astype(str))
    add(f"RAW {name.upper()} MISSING COUNT", missing)
    add(
        f"RAW {name.upper()} MISSING PERCENT",
        (missing / len(frame) * 100).round(2)
    )

for name, df in [
    ("Customers", customers),
    ("Orders", orders),
    ("Products", products),
    ("Tickets", tickets)
]:
    add(f"{name.upper()} MISSING VALUES", df.isna().sum())
    add(f"{name.upper()} DUPLICATE ROWS", df.duplicated().sum())

orders["order_amount"] = pd.to_numeric(orders["order_amount"], errors="coerce")
orders["delivery_minutes"] = pd.to_numeric(orders["delivery_minutes"], errors="coerce")
orders["order_ts"] = pd.to_datetime(orders["order_ts"], errors="coerce")

add("ORDER STATUS COUNTS", orders["status"].value_counts(dropna=False))
add("ORDER AMOUNT SUMMARY", orders["order_amount"].describe())
add("DELIVERY TIME SUMMARY", orders["delivery_minutes"].describe())
add("TOTAL ORDER AMOUNT BY STATUS", orders.groupby("status")["order_amount"].sum().round(2))
add("AVERAGE DELIVERY TIME BY STATUS", orders.groupby("status")["delivery_minutes"].mean().round(2))
add("MONTHLY ORDER COUNTS", orders.groupby(orders["order_ts"].dt.to_period("M").astype(str)).size())

spend = orders[orders["status"].eq("completed")].groupby("customer_id")["order_amount"].sum()
add("TOP 10 CUSTOMERS BY COMPLETED ORDER AMOUNT", spend.sort_values(ascending=False).head(10).round(2))

product_sales = orders.groupby("product_id")["quantity"].sum().reset_index()
product_sales = product_sales.merge(products, on="product_id", how="left")
product_sales = product_sales.sort_values("quantity", ascending=False).head(10)
add("TOP 10 PRODUCTS BY QUANTITY", product_sales)

completed = orders[orders["status"].eq("completed")].copy()
completed = completed.merge(
    customers[["customer_id", "city"]], on="customer_id", how="left"
).merge(
    products[["product_id", "category"]], on="product_id", how="left"
)
pivot = pd.pivot_table(
    completed,
    values="order_amount",
    index="city",
    columns="category",
    aggfunc="sum",
    fill_value=0,
    margins=True,
    margins_name="All",
)
add("CITY BY CATEGORY REVENUE PIVOT (INR)", pivot.round(2))
with sqlite3.connect(os.path.join(base, "data", "instamart.db")) as connection:
    sql_total = pd.read_sql_query(
        "SELECT SUM(order_amount) AS revenue FROM orders "
        "WHERE status = 'completed'",
        connection
    )["revenue"].iloc[0]
pivot_total = float(pivot.loc["All", "All"])
if round(pivot_total, 2) != round(float(sql_total), 2):
    raise AssertionError("Pandas pivot total does not match the SQL total")
add("PIVOT GRAND TOTAL (INR)", round(pivot_total, 2))
add("SQL GRAND TOTAL (INR)", round(float(sql_total), 2))

completed["delivery_minutes"] = pd.to_numeric(
    completed["delivery_minutes"], errors="coerce"
)
city_delivery = completed.groupby("city").agg(
    delivery_sum=("delivery_minutes", "sum"),
    delivery_mean=("delivery_minutes", "mean"),
    delivery_median=("delivery_minutes", "median"),
    delivery_90th_percentile=(
        "delivery_minutes", lambda values: values.quantile(0.9)
    ),
    customer_count=("customer_id", "nunique"),
)
add("COMPLETED DELIVERY AND CUSTOMER METRICS BY CITY", city_delivery.round(2))

report = "\n".join(
    line.rstrip() for block in lines for line in block.splitlines()
).rstrip() + "\n"

path = os.path.join(out, "pandas_analysis_results.txt")
with open(path, "w", encoding="utf-8") as f:
    f.write(report)

print(report)
print(f"\nReport saved to: {path}")