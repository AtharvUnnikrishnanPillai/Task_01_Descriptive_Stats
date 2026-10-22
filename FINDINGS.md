# Task 01: Findings

## Scope and data quality

The supplied Facebook political-ad dataset contains **246,745 records and 40 columns**, including 26 numeric binary classification fields. There are 246,745 distinct ad IDs, with no duplicate IDs or exact duplicate rows. The data contain 4,475 page IDs but 4,546 distinct page names; page names therefore should not be treated as stable identifiers. For example, a single page ID appears under both Biden-Harris HQ and Kamala HQ.

Missing values are concentrated in three columns: delivery stop date (2,159 records; 0.875%), bylines (1,009; 0.409%), and estimated audience size (579; 0.235%). The other columns have no missing values under the documented conventions. Among available dates, no delivery stop precedes its start. Missing stop dates should not automatically be interpreted as zero-duration ads or proof that ads are still active.

## Spending distribution and concentration

Spending is stored as lower/upper ranges, not exact amounts. There are 18 currencies, so totals across the entire file would be misleading without currency conversion. The **246,599 USD records** have closed spending ranges. Their lower bounds sum to **$227,396,100**, and upper bounds sum to **$296,380,401**. The sum of range midpoints is **$261,888,250.50**. This is an illustrative proxy within the aggregate range, not a measured expenditure or a statistical confidence interval. The 146 non-USD records are excluded from these totals.

USD per-ad midpoint spending is strongly right-skewed: the median is **$49.50**, while the mean is **$1,062.00** and sample standard deviation is **$4,993.85**. The midpoint maximum is $474,999.50. The median reflects the common $0–$99 reporting bracket; it does not establish that a typical advertiser spent exactly $49.50.

The largest page-level USD midpoint totals are:

| Page | Records | Midpoint spending proxy |
| --- | ---: | ---: |
| Kamala Harris | 55,503 | $82,823,398.50 |
| Joe Biden | 14,822 | $26,375,389.00 |
| Donald J. Trump | 23,988 | $19,621,356.00 |
| Biden-Harris HQ / Kamala HQ | 9,851 | $10,604,924.50 |
| Tim Walz | 6,581 | $7,637,759.50 |

These are page-level aggregates within this dataset, not complete campaign budgets. Rankings use midpoint proxies and may change under different values within the reported ranges. Row counts describe ad records rather than distinct creatives or people reached.

## Timing, platforms, and labels

Delivery start dates range from **July 6, 2021 to November 5, 2024**, despite the dataset's 2024-election framing. October 2024 accounts for **85,172 starts (34.52%)**, the largest monthly count. This describes the timing of recorded ad starts, not expenditure incurred within the month. The incomplete November period and dataset selection prevent treating its low count as evidence of a general decline.

Platform lists identify Facebook in 238,350 records and Instagram in 223,434. These counts overlap because one record can list multiple platforms. They are not platform-specific spending or audience totals.

The call-to-action label is positive for 141,328 records (57.28%), advocacy for 135,372 (54.86%), issue for 94,170 (38.16%), and attack for 67,079 (27.19%). Among topic labels, economy appears in 30,133 records (12.21%), health in 26,942 (10.92%), and social/cultural in 26,115 (10.58%). Labels can overlap, so percentages should not be added as mutually exclusive categories. A binary field's mean equals its positive-label proportion.

The most frequent exact mention strings include Donald Trump (78,324 records), Kamala Harris (53,239), and Joe Biden (24,247). Aliases such as President Trump and President Biden remain separate in this analysis. Mention counts are nonexclusive and do not imply endorsement, candidate ownership, sentiment, or electoral support.

## Limitations and verification

Impressions have 2,266 open upper bounds; audience size has 100,146. Inventing upper bounds would understate uncertainty, so these records receive no midpoint. Audience sizes cannot be summed into unique people because audiences may overlap. Message content is anonymized, limiting direct verification of classification labels. Fields named `scam` or `Truth` are dataset classifications, not independent proof of misconduct or accuracy.

Both independent summary implementations agree across 475 values within the documented floating-point tolerance. Edge-case tests and an independent integer recomputation of USD spending bounds also passed. Agreement supports computational consistency; it does not resolve selection bias, classification error, or uncertainty in the reported ranges.
