import pandas as pd

customers = pd.read_csv("data/clean/customers.csv")
orders = pd.read_csv("data/clean/orders.csv")

assert len(customers) == 1200
assert customers["city"].nunique() == 6
assert customers["city"].value_counts().to_dict() == {
    "Pune": 227, "Delhi": 210, "Bengaluru": 197,
    "Chennai": 191, "Hyderabad": 191, "Mumbai": 184
}
assert customers["age"].notna().all()
assert customers["age"].between(18, 60).all()
assert customers["gender"].value_counts().to_dict() == {
    "female": 610, "male": 560, "unknown": 30
}
assert len(orders) == 12309
assert orders["order_id"].nunique() == 12309
assert orders["status"].value_counts().to_dict() == {
    "completed": 11110, "cancelled": 1199
}
assert orders["order_amount"].notna().all()
assert orders.loc[orders["status"].eq("completed"), "delivery_minutes"].notna().all()
assert orders.loc[orders["status"].eq("cancelled"), "delivery_minutes"].isna().all()
assert round(orders.loc[orders["status"].eq("completed"), "order_amount"].sum(), 2) == 2998668.80

print("ALL CHECKPOINTS PASSED")
