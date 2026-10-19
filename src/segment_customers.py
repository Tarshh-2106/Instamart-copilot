import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
inp = os.path.join(base, "outputs", "rfm_features.csv")
out = os.path.join(base, "outputs")

rfm = pd.read_csv(inp)

features = ["recency", "frequency", "monetary"]
x = rfm[features].copy()
x["recency"] = x["recency"].clip(lower=0)
x["frequency"] = x["frequency"].clip(lower=1)
x["monetary"] = x["monetary"].clip(lower=0)

model = Pipeline([
    ("scale", StandardScaler()),
    ("kmeans", KMeans(n_clusters=4, random_state=42, n_init=10))
])

rfm["segment"] = model.fit_predict(x)

centres = rfm.groupby("segment")[features].mean().round(2)
counts = rfm["segment"].value_counts().sort_index()

print("Customers per segment:")
print(counts)
print("\nAverage RFM values per segment:")
print(centres)

pca = PCA(n_components=2)
z = StandardScaler().fit_transform(x)
points = pca.fit_transform(z)

rfm["pca1"] = points[:, 0]
rfm["pca2"] = points[:, 1]

plt.figure(figsize=(9, 6))
for seg in sorted(rfm["segment"].unique()):
    d = rfm[rfm["segment"] == seg]
    plt.scatter(d["pca1"], d["pca2"], label=f"Segment {seg}", alpha=0.7)

plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")
plt.title("Customer Segmentation using RFM and K-Means")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(out, "customer_segments_pca.png"), dpi=200)
plt.close()

rfm.to_csv(os.path.join(out, "customer_segments.csv"), index=False)
centres.to_csv(os.path.join(out, "segment_summary.csv"))

print("\nSaved outputs/customer_segments.csv")
print("Saved outputs/segment_summary.csv")
print("Saved outputs/customer_segments_pca.png")