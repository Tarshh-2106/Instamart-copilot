
import os

folder = "data/policies"

for name in sorted(os.listdir(folder)):
    path = os.path.join(folder, name)

    if not os.path.isfile(path) or not name.endswith(".txt"):
        continue

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    with open(path, "r", encoding="utf-8") as f:
        print(f.read())
