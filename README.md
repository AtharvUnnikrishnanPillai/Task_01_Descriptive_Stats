# Task 01: Descriptive Statistics

This project analyzes `fb_ads_president_scored_anon.csv` using independent standard-library Python and Pandas implementations. Each produces descriptive statistics for every column. A separate analysis interprets spending ranges, dates, platform lists, and classification labels.

## Dataset

Download the [assignment dataset](https://drive.google.com/file/d/1gvtvX8fATFrrzraPmTSf205U8u3JExUR/view?usp=sharing) and place it locally at `data/fb_ads_president_scored_anon.csv`. Create the `data` folder if necessary. The CSV is deliberately excluded from this repository, as required by the assignment.

The analyzed file contains 246,745 rows and 40 columns. Its SHA-256 is recorded in both JSON summaries so results can be tied to the exact input.

## Run

Use Python 3.11 or later. From this repository's root:

```bash
python -m pip install -r requirements.txt
python pure_python_stats.py data/fb_ads_president_scored_anon.csv
python pandas_stats.py data/fb_ads_president_scored_anon.csv
python compare_results.py
python analyze_ads.py data/fb_ads_president_scored_anon.csv
python -m unittest -v test_stats
```

The pure Python script requires no external packages. Pandas is needed for the other analysis and the cross-implementation tests. Scripts accept an input path and `--out` JSON output path. Default outputs go into `results/`.

## Statistical conventions

- Trim whitespace; treat empty strings, NA, N/A, null, none, and nan as missing, case-insensitively. Counts exclude these markers; missing percentages use all rows.
- Infer a numeric column only when every nonmissing value converts to a finite number. Remove commas and a leading dollar sign; recognize accounting parentheses. A mixed numeric/text column remains categorical rather than silently losing invalid entries.
- Treat identifiers and scored-message hashes as categorical. Classify ISO date strings separately and summarize their frequencies.
- Numeric statistics: count, mean, minimum, maximum, median, and **sample** standard deviation (`n - 1`). Singleton standard deviations are null.
- Nonnumeric statistics: nonmissing count, unique count, mode, mode frequency, and five most frequent values. Resolve ties alphabetically. Empty columns have zero unique values and no mode.
- The canonical JSON comparison uses exact counts/categories and a floating-point tolerance of `1e-10`. Native Pandas `describe()` tables are supplementary; their tied mode choice may differ from the canonical alphabetical rule.
- Raw range/list columns receive categorical summaries. `analyze_ads.py` additionally parses them with `ast.literal_eval`, reports endpoint statistics and open ranges, and analyzes USD spending separately. Midpoints are calculated only for closed ranges.

## Files and findings

`pure_python_stats.py` and `pandas_stats.py` implement independent summaries; `compare_results.py` checks agreement. `analyze_ads.py` produces contextual findings. `test_stats.py` checks known answers and edge cases. `results/` contains generated evidence, including the comparison result and runtime versions.

See `FINDINGS.md` for interpretation and `COMPARISON.md` for implementation tradeoffs. Key results: 4,475 distinct page IDs, 18 currencies, and USD spending bounds totaling $227.40–$296.38 million. All 475 compared values matched within the documented tolerance.

## Submission

Create a GitHub repository named `Task_01_Descriptive_Stats`. Upload these source files, Markdown files, requirements, and generated results. Do not upload the raw CSV or the local `data/` folder. GitHub's web uploader does not enforce `.gitignore`, so exclude the CSV manually when using the browser. Submit the repository link through the assignment's required channel.

## Assistance disclosure

These scripts and drafts were prepared with AI assistance and executed against the supplied CSV. The submitter should review the code, reproduce the commands, and adapt the written reflection to accurately describe their own work. No unperformed activity or time spent is claimed.
