
import os
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score
)
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.utils import resample

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base, "data", "clean")
out_dir = os.path.join(base, "outputs")

os.makedirs(out_dir, exist_ok=True)

orders = pd.read_csv(os.path.join(data_dir, "orders.csv"))
customers = pd.read_csv(os.path.join(data_dir, "customers.csv"))
segments = pd.read_csv(os.path.join(out_dir, "customer_segments.csv"))

orders["order_ts"] = pd.to_datetime(orders["order_ts"], errors="coerce")
orders["order_amount"] = pd.to_numeric(orders["order_amount"], errors="coerce")

orders = orders[orders["status"].eq("completed")].copy()
orders = orders.dropna(subset=["customer_id", "order_ts"])

start_date = pd.Timestamp("2025-04-01")
cutoff = pd.Timestamp("2025-09-01")
end_date = pd.Timestamp("2025-10-01")

hist = orders[
    (orders["order_ts"] >= start_date) &
    (orders["order_ts"] < cutoff)
].copy()

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

features["recency"] = (cutoff - features["last_order"].dt.normalize()).dt.days
features = features.drop(columns=["last_order"])

future_customers = set(future["customer_id"].unique())
features["lapsed"] = (~features.index.isin(future_customers)).astype(int)

features = features.reset_index()
features = features.merge(customers, on="customer_id", how="left")

features["age"] = pd.to_numeric(features["age"], errors="coerce")
features["city"] = features["city"].fillna("Unknown")
features["gender"] = features["gender"].fillna("Unknown")

segments = segments[["customer_id", "segment_name", "is_premium"]].copy()
features = features.merge(segments, on="customer_id", how="left")
features["is_premium"] = features["is_premium"].fillna(False).astype(bool)

num_cols = [
    "recency",
    "frequency",
    "monetary",
    "avg_order_value",
    "age"
]
cat_cols = ["city", "gender"]

x = features[num_cols + cat_cols]
y = features["lapsed"]

if y.nunique() < 2:
    raise ValueError("The lapse target has only one class.")

x_train, x_test, y_train, y_test = train_test_split(
    x,
    y,
    test_size=0.2,
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
        ("encode", OneHotEncoder(handle_unknown="ignore"))
    ]), cat_cols)
])

models = {
    "Logistic Regression": (
        Pipeline([
            ("prep", prep),
            ("clf", LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=42
            ))
        ]),
        {
            "clf__C": [0.1, 1, 10]
        }
    ),
    "Random Forest": (
        Pipeline([
            ("prep", prep),
            ("clf", RandomForestClassifier(
                random_state=42,
                class_weight="balanced"
            ))
        ]),
        {
            "clf__n_estimators": [100, 200],
            "clf__max_depth": [None, 10],
            "clf__min_samples_leaf": [1, 5]
        }
    )
}

results = []
best_name = None
best_search = None
best_f1 = -1

for name, (pipe, params) in models.items():
    search = GridSearchCV(
        pipe,
        params,
        scoring="f1",
        cv=5,
        n_jobs=-1
    )
    search.fit(x_train, y_train)

    pred = search.predict(x_test)
    prob = search.predict_proba(x_test)[:, 1]
    score = f1_score(y_test, pred, zero_division=0)

    results.append({
        "model": name,
        "best_cv_f1": round(search.best_score_, 4),
        "test_accuracy": round(accuracy_score(y_test, pred), 4),
        "test_precision": round(precision_score(y_test, pred, zero_division=0), 4),
        "test_recall": round(recall_score(y_test, pred, zero_division=0), 4),
        "test_f1": round(score, 4),
        "test_roc_auc": round(roc_auc_score(y_test, prob), 4),
        "best_params": str(search.best_params_)
    })

    print(f"\n{name}")
    print("Best parameters:", search.best_params_)
    print("Test F1:", round(score, 4))
    print("Test ROC-AUC:", round(roc_auc_score(y_test, prob), 4))
    print(classification_report(y_test, pred, zero_division=0))
    print("Confusion matrix:")
    print(confusion_matrix(y_test, pred))

    if score > best_f1:
        best_f1 = score
        best_name = name
        best_search = search

comparison = pd.DataFrame(results)
comparison.to_csv(os.path.join(out_dir, "lapse_model_comparison.csv"), index=False)

print("\nModel comparison:")
print(comparison.to_string(index=False))
print("\nSelected model:", best_name)

best_model = best_search.best_estimator_
joblib.dump(best_model, os.path.join(out_dir, "lapse_model.joblib"))

pred_all = best_model.predict(x)
prob_all = best_model.predict_proba(x)[:, 1]

features["lapse_probability"] = prob_all
features["predicted_lapse"] = pred_all

features.sort_values("lapse_probability", ascending=False).to_csv(
    os.path.join(out_dir, "lapse_predictions.csv"),
    index=False
)

retention = features[features["predicted_lapse"].eq(1)].copy()
retention = retention.sort_values("lapse_probability", ascending=False)
retention.to_csv(os.path.join(out_dir, "retention_list.csv"), index=False)

minority = y_train.value_counts().idxmin()
majority = y_train.value_counts().idxmax()

train = x_train.copy()
train["lapsed"] = y_train.values

majority_rows = train[train["lapsed"] == majority]
minority_rows = train[train["lapsed"] == minority]

minority_up = resample(
    minority_rows,
    replace=True,
    n_samples=len(majority_rows),
    random_state=42
)

balanced = pd.concat([majority_rows, minority_up]).sample(
    frac=1,
    random_state=42
)

x_bal = balanced.drop(columns=["lapsed"])
y_bal = balanced["lapsed"]

balanced_model = best_model.__class__(
    steps=best_model.steps
)
balanced_model.fit(x_bal, y_bal)

bal_pred = balanced_model.predict(x_test)
bal_prob = balanced_model.predict_proba(x_test)[:, 1]

print("\nOversampling experiment using selected model")
print("Original training class counts:")
print(y_train.value_counts().sort_index().to_dict())
print("Balanced training class counts:")
print(y_bal.value_counts().sort_index().to_dict())
print("Oversampled test F1:", round(f1_score(y_test, bal_pred, zero_division=0), 4))
print("Oversampled test ROC-AUC:", round(roc_auc_score(y_test, bal_prob), 4))
print(classification_report(y_test, bal_pred, zero_division=0))

pd.DataFrame([{
    "experiment": "Random oversampling",
    "model": best_name,
    "test_f1": round(f1_score(y_test, bal_pred, zero_division=0), 4),
    "test_roc_auc": round(roc_auc_score(y_test, bal_prob), 4)
}]).to_csv(os.path.join(out_dir, "lapse_resampling_results.csv"), index=False)

prep_fit = best_model.named_steps["prep"]
clf = best_model.named_steps["clf"]

feature_names = prep_fit.get_feature_names_out()

if hasattr(clf, "feature_importances_"):
    importance = clf.feature_importances_
    explanation = "Random Forest feature importance"
else:
    importance = abs(clf.coef_[0])
    explanation = "Absolute Logistic Regression coefficients"

importance_df = pd.DataFrame({
    "feature": feature_names,
    "importance": importance
}).sort_values("importance", ascending=False)

importance_df.to_csv(
    os.path.join(out_dir, "lapse_feature_importance.csv"),
    index=False
)

print("\nFeature interpretation:", explanation)
print(importance_df.head(15).to_string(index=False))

print("\nFeature window:", start_date.date(), "to", (cutoff - pd.Timedelta(days=1)).date())
print("Observation window:", cutoff.date(), "to", (end_date - pd.Timedelta(days=1)).date())
print("Customers:", len(features))
print("Lapsed:", int(y.sum()))
print("Not lapsed:", int((y == 0).sum()))
print("Training rows:", len(x_train))
print("Test rows:", len(x_test))
print("\nSaved outputs/lapse_model.joblib")
print("Saved outputs/lapse_predictions.csv")
print("Saved outputs/retention_list.csv")
print("Saved outputs/lapse_model_comparison.csv")
print("Saved outputs/lapse_resampling_results.csv")
print("Saved outputs/lapse_feature_importance.csv")
