
import os
import pandas as pd

p = "data/raw"

for f in os.listdir(p):
    if f.endswith(".csv"):
        d = pd.read_csv(os.path.join(p, f))
        print(f"{f}: {d.shape[0]} rows, {d.shape[1]} columns")
