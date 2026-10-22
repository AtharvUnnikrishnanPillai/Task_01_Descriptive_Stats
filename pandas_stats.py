"""Independent Pandas implementation of the documented summary contract."""
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd

MISSING = {"", "na", "n/a", "null", "none", "nan"}


def summarize(path, describe_dir=None):
    frame = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    frame = frame.apply(lambda column: column.str.strip())
    frame = frame.mask(frame.apply(lambda column: column.str.casefold().isin(MISSING)))
    print("Shape:", frame.shape)
    print("Raw dtypes (strings retained intentionally):\n", frame.dtypes)
    frame.info()
    result = {"rows": len(frame), "column_count": len(frame.columns), "columns": {}}
    typed = frame.copy()
    numeric_names = []
    for name in frame:
        series = frame[name].dropna()
        cleaned = series.str.replace(",", "", regex=False).str.replace(r"^\$", "", regex=True)
        cleaned = cleaned.str.replace(r"^\((.*)\)$", r"-\1", regex=True)
        numbers = pd.to_numeric(cleaned, errors="coerce").replace([float("inf"), -float("inf")], float("nan"))
        identifier = name.lower().endswith("_id") or name == "illuminating_scored_message"
        numeric = bool(len(series)) and not identifier and numbers.notna().all()
        dates = (not identifier and len(series) > 0 and
                 series.str.fullmatch(r"\d{4}-\d{2}-\d{2}").all() and
                 pd.to_datetime(series, format="%Y-%m-%d", errors="coerce").notna().all())
        kind = "empty" if series.empty else "numeric" if numeric else "date" if dates else "categorical"
        item = {"type": kind, "count": int(series.count()), "missing": int(frame[name].isna().sum()),
                "missing_pct": float(frame[name].isna().mean() * 100) if len(frame) else 0}
        if numeric:
            typed[name] = pd.to_numeric(frame[name], errors="coerce")
            # Use the explicitly cleaned numeric values, including any currencies/commas.
            typed[name] = numbers.reindex(frame.index)
            numeric_names.append(name)
            item.update(mean=float(numbers.mean()), min=float(numbers.min()), max=float(numbers.max()),
                        std=float(numbers.std(ddof=1)) if len(numbers) > 1 else None,
                        median=float(numbers.median()))
        else:
            frequency = series.value_counts()
            top = sorted(frequency.items(), key=lambda pair: (-pair[1], pair[0]))[:5]
            item.update(unique=int(series.nunique()), mode=top[0][0] if top else None,
                        mode_frequency=int(top[0][1]) if top else 0,
                        top5=[[value, int(count)] for value, count in top])
        result["columns"][name] = item
    numeric_describe = typed[numeric_names].describe() if numeric_names else pd.DataFrame()
    other = [name for name in frame if name not in numeric_names]
    categorical_describe = frame[other].describe(include="all") if other else pd.DataFrame()
    print("\nNumeric describe:\n", numeric_describe.to_string())
    print("\nNon-numeric describe:\n", categorical_describe.to_string())
    if describe_dir:
        describe_dir.mkdir(parents=True, exist_ok=True)
        numeric_describe.to_csv(describe_dir / "pandas_numeric_describe.csv")
        categorical_describe.to_csv(describe_dir / "pandas_categorical_describe.csv")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--out", type=Path, default=Path("results/pandas.json"))
    args = parser.parse_args()
    result = summarize(args.csv_path, args.out.parent)
    with args.csv_path.open("rb") as handle:
        result["sha256"] = hashlib.file_digest(handle, "sha256").hexdigest()
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
