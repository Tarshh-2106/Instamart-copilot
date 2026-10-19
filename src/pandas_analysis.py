import os
import pandas as pd

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = os.path.join(base, "data", "clean")
out = os.path.join(base, "outputs")

os.makedirs(out, exist_ok=True)

customers = pd.read_csv(os.path.join(data, "customers.csv"))
orders = pd.read_csv(os.path.join(data, "orders.csv"))
products = pd.read_csv(os.path.join(data, "products.csv"))
tickets = pd.read_csv(os.path.join(data, "tickets.csv"))

lines = []

def add(title, value):
    lines.append(f"\n{title}\n")
    lines.append(str(value))
    lines.append("\n")

add("DATASET SHAPES", {
    "customers": customers.shape,
    "orders": orders.shape,
    "products": products.shape,
    "tickets": tickets.shape
})

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

report = "\n".join(lines)

path = os.path.join(out, "pandas_analysis_results.txt")
with open(path, "w", encoding="utf-8") as f:
    f.write(report)

print(report)
print(f"\nReport saved to: {path}")