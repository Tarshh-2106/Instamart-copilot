
import os
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
inp = os.path.join(base, "outputs", "rfm_features.csv")
out = os.path.join(base, "outputs")

os.makedirs(out, exist_ok=True)

rfm = pd.read_csv(inp)

features = ["recency", "frequency", "monetary"]
x = rfm[features].copy()
x["recency"] = x["recency"].clip(lower=0)
x["frequency"] = x["frequency"].clip(lower=1)
x["monetary"] = x["monetary"].clip(lower=0)

scaler = StandardScaler()
z = scaler.fit_transform(x)

results = []

for k in range(2, 9):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(z)
    results.append({
        "k": k,
        "inertia": round(km.inertia_, 2),
        "silhouette": round(silhouette_score(z, labels), 4)
    })

evaluation = pd.DataFrame(results)
evaluation.to_csv(os.path.join(out, "cluster_evaluation.csv"), index=False)

print("Cluster evaluation:")
print(evaluation.to_string(index=False))

km = KMeans(n_clusters=4, random_state=42, n_init=10)
rfm["segment"] = km.fit_predict(z)

centres = rfm.groupby("segment")[features].mean()
high_spend = centres["monetary"].idxmax()
remaining = centres.drop(index=high_spend)

lapsed = remaining["recency"].idxmax()
remaining = remaining.drop(index=lapsed)

frequent = remaining["frequency"].idxmax()
occasional = remaining.index.difference([frequent])[0]

names = {
    lapsed: "Lapsed / High Risk",
    occasional: "Occasional Customers",
    frequent: "Frequent Recent Customers",
    high_spend: "High Spending / Premium"
}

actions = {
    lapsed: "Send a win-back offer and targeted reactivation message.",
    occasional: "Encourage repeat purchases with relevant recommendations.",
    frequent: "Reward loyalty and encourage continued engagement.",
    high_spend: "Provide premium retention offers and personalized service."
}

rfm["segment_name"] = rfm["segment"].map(names)
rfm["recommended_action"] = rfm["segment"].map(actions)
rfm["is_premium"] = rfm["segment"].eq(high_spend)

print("\nCustomers per segment:")
print(rfm["segment_name"].value_counts())

print("\nSegment profiles:")
print(
    rfm.groupby("segment_name")[features + ["is_premium"]]
    .agg({
        "recency": "mean",
        "frequency": "mean",
        "monetary": "mean",
        "is_premium": "sum"
    }).round(2).to_string()
)

pca = PCA(n_components=2)
points = pca.fit_transform(z)

rfm["pca1"] = points[:, 0]
rfm["pca2"] = points[:, 1]

rfm.to_csv(os.path.join(out, "customer_segments.csv"), index=False)

rfm.groupby("segment_name")[features].mean().round(2).to_csv(
    os.path.join(out, "segment_summary.csv")
)

print("\nPCA explained variance ratio:", pca.explained_variance_ratio_.round(4))
print("Saved outputs/customer_segments.csv")
print("Saved outputs/segment_summary.csv")
print("Saved outputs/cluster_evaluation.csv")
