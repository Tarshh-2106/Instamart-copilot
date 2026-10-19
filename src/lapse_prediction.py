import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    accuracy_score
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base, "data", "clean")
out_dir = os.path.join(base, "outputs")
model_dir = os.path.join(base, "models")

os.makedirs(out_dir, exist_ok=True)
os.makedirs(model_dir, exist_ok=True)

orders = pd.read_csv(os.path.join(data_dir, "orders.csv"))
customers = pd.read_csv(os.path.join(data_dir, "customers.csv"))

orders["order_ts"] = pd.to_datetime(orders["order_ts"], errors="coerce")
orders["order_amount"] = pd.to_numeric(orders["order_amount"], errors="coerce")

orders = orders[orders["status"].eq("completed")].copy()
orders = orders.dropna(subset=["customer_id", "order_ts"])

cutoff = pd.Timestamp("2025-08-01")
end_date = pd.Timestamp("2025-10-01")

hist = orders[orders["order_ts"] < cutoff].copy()
future = orders[
    (orders["order_ts"] >= cutoff) &
    (orders["order_ts"] < end_date)
].copy()

features = hist.groupby("customer_id").agg(
    last_order=("order_ts", "max"),
    frequency=("order_id", "nunique"),
    monetary=("order_amount", "sum"),
    avg_order_value=("order_amount", "mean")
)

features["recency"] = (cutoff - features["last_order"]).dt.days
features = features.drop(columns=["last_order"])

future_customers = set(future["customer_id"].unique())
features["lapsed"] = (~features.index.isin(future_customers)).astype(int)

features = features.reset_index()
features = features.merge(customers, on="customer_id", how="left")

features["age"] = pd.to_numeric(features["age"], errors="coerce")
features["city"] = features["city"].fillna("Unknown")
features["gender"] = features["gender"].fillna("Unknown")

num_cols = ["recency", "frequency", "monetary", "avg_order_value", "age"]
cat_cols = ["city", "gender"]

x = features[num_cols + cat_cols]
y = features["lapsed"]

if y.nunique() < 2:
    raise ValueError("The lapse target has only one class; cannot train classifier.")

x_train, x_test, y_train, y_test = train_test_split(
    x,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

prep = ColumnTransformer([
    ("num", Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scale", StandardScaler())
    ]), num_cols),
    ("cat", Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encode", __import__("sklearn").preprocessing.OneHotEncoder(handle_unknown="ignore"))
    ]), cat_cols)
])

model = Pipeline([
    ("prep", prep),
    ("clf", LogisticRegression(max_iter=2000, class_weight="balanced"))
])

model.fit(x_train, y_train)

pred = model.predict(x_test)
prob = model.predict_proba(x_test)[:, 1]

print("Feature window:", hist["order_ts"].min(), "to", hist["order_ts"].max())
print("Observation window:", cutoff.date(), "to", (end_date - pd.Timedelta(days=1)).date())
print("Customers:", len(features))
print("Lapsed:", int(y.sum()))
print("Not lapsed:", int((y == 0).sum()))
print("Accuracy:", round(accuracy_score(y_test, pred), 4))
print("ROC-AUC:", round(roc_auc_score(y_test, prob), 4))
print("\nClassification report:")
print(classification_report(y_test, pred, zero_division=0))
print("Confusion matrix:")
print(confusion_matrix(y_test, pred))

features["lapse_probability"] = model.predict_proba(x)[:, 1]
features["predicted_lapse"] = (features["lapse_probability"] >= 0.5).astype(int)

features.sort_values("lapse_probability", ascending=False).to_csv(
    os.path.join(out_dir, "lapse_predictions.csv"), index=False
)

features[features["predicted_lapse"].eq(1)].sort_values(
    "lapse_probability", ascending=False
).to_csv(os.path.join(out_dir, "retention_targets.csv"), index=False)

joblib.dump(model, os.path.join(model_dir, "lapse_model.joblib"))

plt.figure(figsize=(7, 5))
features["lapsed"].value_counts().sort_index().plot(kind="bar")
plt.xticks([0, 1], ["Active later", "Lapsed"], rotation=0)
plt.ylabel("Customers")
plt.title("Historical Lapse Target Distribution")
plt.tight_layout()
plt.savefig(os.path.join(out_dir, "lapse_target_distribution.png"), dpi=200)
plt.close()

print("\nSaved outputs/lapse_predictions.csv")
print("Saved outputs/retention_targets.csv")
print("Saved outputs/lapse_target_distribution.png")
print("Saved models/lapse_model.joblib")