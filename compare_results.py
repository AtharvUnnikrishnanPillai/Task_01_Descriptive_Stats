"""Compare all nested summary fields; counts and categories must match exactly."""
import argparse
import json
import math
from pathlib import Path


def compare(a, b, location="root"):
    if isinstance(a, dict) and isinstance(b, dict):
        assert a.keys() == b.keys(), f"Keys differ at {location}"
        return sum(compare(a[k], b[k], f"{location}.{k}") for k in a)
    if isinstance(a, list) and isinstance(b, list):
        assert len(a) == len(b), f"Length differs at {location}"
        return sum(compare(x, y, f"{location}[{i}]") for i, (x, y) in enumerate(zip(a, b)))
    if isinstance(a, float) or isinstance(b, float):
        assert a is not None and b is not None and math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-10), (location, a, b)
    else:
        assert a == b, (location, a, b)
    return 1


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("pure", nargs="?", default="results/pure_python.json")
    p.add_argument("pandas", nargs="?", default="results/pandas.json")
    args = p.parse_args()
    n = compare(json.loads(Path(args.pure).read_text()), json.loads(Path(args.pandas).read_text()))
    result = {"status": "PASS", "leaf_values_compared": n, "relative_tolerance": 1e-10, "absolute_tolerance": 1e-10}
    Path("results/comparison.json").write_text(json.dumps(result, indent=2))
    print(result)
