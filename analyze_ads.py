"""Interpret structured ad fields without inventing missing range endpoints."""
import argparse
import ast
import json
from collections import Counter
from pathlib import Path
import pandas as pd


def analyze(path):
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    result = {"rows": len(df), "duplicate_ad_ids": int(df.ad_id.duplicated().sum()),
              "duplicate_rows": int(df.duplicated().sum()),
              "currencies": df.currency.value_counts().to_dict(), "ranges": {}}
    for name in ["spend", "impressions", "estimated_audience_size"]:
        bounds = []
        missing = invalid = 0
        for raw in df[name]:
            if raw.strip().lower() in {"", "na", "n/a", "null", "none", "nan"}:
                missing += 1
                bounds.append((None, None))
                continue
            try:
                value = ast.literal_eval(raw)
                lo = float(value["lower_bound"]) if "lower_bound" in value else None
                hi = float(value["upper_bound"]) if "upper_bound" in value else None
                if lo is None or lo < 0 or (hi is not None and hi < lo):
                    raise ValueError("Invalid bounds")
                bounds.append((lo, hi))
            except (ValueError, TypeError, SyntaxError, KeyError):
                invalid += 1
                bounds.append((None, None))
        b = pd.DataFrame(bounds, columns=[name + "_lower", name + "_upper"])
        df = pd.concat([df, b], axis=1)
        mid = (b.iloc[:, 0] + b.iloc[:, 1]) / 2
        df[name + "_midpoint"] = mid
        result["ranges"][name] = {
            "missing": missing, "invalid": invalid,
            "open_upper": int((b.iloc[:, 0].notna() & b.iloc[:, 1].isna()).sum()),
            "closed": int(mid.notna().sum()),
            "endpoint_describe": b.describe().to_dict()}
    usd = df.loc[df.currency.eq("USD")]
    result["usd"] = {"rows": len(usd),
                     "closed_spend_rows": int(usd.spend_midpoint.notna().sum()),
                     "lower_total": float(usd.spend_lower.sum()),
                     "upper_total_closed_only": float(usd.spend_upper.sum()),
                     "midpoint_total_closed_only": float(usd.spend_midpoint.sum()),
                     "midpoint_describe": usd.spend_midpoint.describe().to_dict()}
    pages = usd.groupby("page_id").agg(rows=("ad_id", "size"),
                                        midpoint=("spend_midpoint", "sum"))
    pages["names"] = usd.groupby("page_id").page_name.agg(lambda s: " / ".join(sorted(set(s))))
    result["usd_top_pages"] = pages.sort_values("midpoint", ascending=False).head(10).reset_index().to_dict("records")
    result["lists"] = {}
    for col in ["illuminating_mentions", "publisher_platforms"]:
        counts = Counter()
        invalid = 0
        for raw in df[col]:
            try:
                values = ast.literal_eval(raw)
                if not isinstance(values, list) or not all(isinstance(x, str) for x in values):
                    raise ValueError("Expected string list")
                counts.update(set(values))
            except (ValueError, SyntaxError, TypeError):
                invalid += 1
        result["lists"][col] = {"invalid": invalid, "counts": dict(counts.most_common())}
    result["dates"] = {}
    for col in ["ad_creation_time", "ad_delivery_start_time", "ad_delivery_stop_time"]:
        dt = pd.to_datetime(df[col], errors="coerce")
        result["dates"][col] = {"min": str(dt.min().date()), "max": str(dt.max().date()),
                                  "missing_or_invalid": int(dt.isna().sum())}
    start = pd.to_datetime(df.ad_delivery_start_time, errors="coerce")
    stop = pd.to_datetime(df.ad_delivery_stop_time, errors="coerce")
    result["stop_before_start"] = int((stop < start).sum())
    result["start_month_counts"] = start.dt.strftime("%Y-%m").value_counts().sort_index().to_dict()
    result["positive_labels"] = {col: int(df[col].eq("1").sum()) for col in df
                                  if col.startswith("illuminating_") and
                                  col not in {"illuminating_mentions", "illuminating_scored_message"}}
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--out", type=Path, default=Path("results/ad_analysis.json"))
    args = parser.parse_args()
    result = analyze(args.csv_path)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    print(args.out)
