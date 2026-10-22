# Pure Python and Pandas comparison

## Agreement

Both implementations independently read the same CSV and calculate summaries. Neither imports statistical calculations from the other. Their SHA-256 input hashes match. The recursive comparison passed for all **475 leaf values**, including shape, inferred types, nonmissing/missing counts, numeric statistics, categorical frequencies, and the input hash. Categories and integer counts must match exactly; floating-point results use relative and absolute tolerances of `1e-10`.

Both use sample standard deviation. This explicit choice avoids a common disagreement between population formulas and Pandas' default `ddof=1`. Whitespace, missing markers, numeric cleaning, identifier handling, and alphabetical frequency tie-breaking are also specified identically. Pandas' supplementary `describe()` output may choose a different representative among equally frequent categories; the canonical comparison controls this explicitly.

Two automated tests passed: one checks manually known numeric answers, including a singleton and an empty numeric sequence; the other checks both implementations on a fixture containing missing markers, currency-formatted numbers, a negative accounting value, invalid mixed text, tied categories, numeric-looking identifiers, and zeros. These checks provide evidence beyond having two implementations agree on the supplied dataset.

## Implementation tradeoffs

The standard-library implementation makes the mechanics visible: CSV parsing, type inference, counting, sorting for a median, and the sample variance formula are explicit. It runs without third-party dependencies and is useful for understanding the calculations. Its column lists and sorted copies consume memory, however; this implementation is not a streaming solution for arbitrarily large files.

Pandas expresses aggregation more concisely through `count`, `mean`, `std`, `median`, `value_counts`, and `nunique`. Its `info()` and `describe()` outputs help inspect the data quickly. Loading as strings first preserves identifiers and missing-value conventions, but introduces additional cleaning steps. The DataFrame and intermediate copies also consume memory.

No controlled timing or peak-memory benchmark was performed, so this project does not claim that one implementation was faster or used less memory. The demonstrated tradeoff is explicit control versus concise tabular operations.

## Interpretation choices

Matching calculations cannot by itself establish valid interpretation. Spending and exposure fields contain intervals rather than observed exact values. Accordingly, a separate contextual analysis preserves missing upper bounds and keeps currencies separate. Page IDs are used for page-level spending because page names can change. Classification flags are reported as labels, without claiming independent verification of their truth.

For further work, a schema-aware validator, chunked processing, and a curated candidate-alias mapping would improve robustness. Changes to inferred types or missing-value conventions would need to be applied to both implementations and documented before comparing their results.
