"""Describe every CSV column with the standard library only."""
import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import date
from pathlib import Path

MISSING = {"", "na", "n/a", "null", "none", "nan"}


def number(value):
    """Explicit cleaning: commas, leading $, and accounting parentheses."""
    text = value.replace(",", "").removeprefix("$")
    if text.startswith("(") and text.endswith(")"):
        text = "-" + text[1:-1]
    try:
        result = float(text)
        return result if math.isfinite(result) else None
    except ValueError:
        return None


def numeric_stats(values):
    n = len(values)
    if not n:
        return dict(count=0, mean=None, min=None, max=None, std=None, median=None)
    ordered = sorted(values)
    mean = math.fsum(values) / n
    median = ordered[n // 2] if n % 2 else (ordered[n // 2 - 1] + ordered[n // 2]) / 2
    variance = math.fsum((x - mean) ** 2 for x in values) / (n - 1) if n > 1 else None
    return dict(count=n, mean=mean, min=ordered[0], max=ordered[-1],
                std=math.sqrt(variance) if variance is not None else None, median=median)


def is_date(value):
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def summarize(path):
    with open(path, encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        if len(set(header)) != len(header):
            raise ValueError("Duplicate column names")
        columns = [[] for _ in header]
        rows = 0
        for line, row in enumerate(reader, 2):
            if len(row) != len(header):
                raise ValueError(f"CSV record {line}: expected {len(header)} fields, got {len(row)}")
            rows += 1
            for values, value in zip(columns, row):
                values.append(value.strip())
    result = {"rows": rows, "column_count": len(header), "columns": {}}
    for name, raw in zip(header, columns):
        values = [x for x in raw if x.casefold() not in MISSING]
        converted = [number(x) for x in values]
        # Identifier semantics take precedence over numeric-looking strings.
        identifier = name.lower().endswith("_id") or name == "illuminating_scored_message"
        numeric = bool(values) and not identifier and all(x is not None for x in converted)
        kind = ("empty" if not values else "numeric" if numeric else
                "date" if not identifier and all(is_date(x) for x in values) else "categorical")
        item = {"type": kind, "count": len(values), "missing": rows - len(values),
                "missing_pct": 100 * (rows - len(values)) / rows if rows else 0}
        if numeric:
            item.update(numeric_stats(converted))
        else:
            frequency = Counter(values)
            top = sorted(frequency.items(), key=lambda pair: (-pair[1], pair[0]))[:5]
            item.update(unique=len(frequency), mode=top[0][0] if top else None,
                        mode_frequency=top[0][1] if top else 0, top5=[list(x) for x in top])
        result["columns"][name] = item
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--out", type=Path, default=Path("results/pure_python.json"))
    args = parser.parse_args()
    result = summarize(args.csv_path)
    with args.csv_path.open("rb") as handle:
        result["sha256"] = hashlib.file_digest(handle, "sha256").hexdigest()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)
    args.out.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
