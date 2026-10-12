# LinkedIn campaign CTR analysis

A Python notebook for comparing campaign click-through rates using Wilson confidence intervals, two-proportion z-tests, and exploratory time-series plots.

## Explore

- [Notebook](LinkedIn%20AB%20Test%20%28copy%29%20%282%29.ipynb): executable analysis.
- [Saved HTML report](index.html): historical output from the original analysis. It has not been regenerated from the corrected notebook and should not be used as the updated result.
- [analysis.py](analysis.py): validated campaign aggregation and pairwise comparisons.

## Run locally

Use Python 3.10 or newer from the repository root:

```bash
git clone https://github.com/derrickbaruga7/LinkedIn-AB-test-notebook.git
cd LinkedIn-AB-test-notebook
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
jupyter lab
```

On Windows, activate with `.venv\Scripts\activate` instead. Open the notebook and run its cells in order.

## Input reports

Campaign exports are **not included**. Put authorized reports in `data/`, or set `LINKEDIN_REPORT_DIR` before launching Jupyter. Filenames must match `*creative_performance_report*.csv`. The loader expects UTF-16-LE, tab-separated exports with five metadata lines before the header.

Required columns normalize to `campaign_name`, `clicks_to_landing_page`, `impressions`, and `start_date_in_utc`. Dates use month/day/year. Clicks and impressions must be nonnegative whole numbers, and clicks cannot exceed impressions. Zero-impression campaigns are excluded from rate comparisons. Avoid overlapping exports: concatenation does not deduplicate them.

## Statistical interpretation

Campaign summaries aggregate clicks and impressions before calculating CTR. Pairwise comparisons apply Holm correction within each displayed comparison table. Pre/post tables independently aggregate their own observations around July 25, 2025.

The split date is an exploratory choice, not evidence of a platform algorithm change. Campaign differences alone do not establish causality or random assignment. Z-tests rely on adequate counts and a binomial approximation; repeated viewers and differing audiences can violate independence. Daily-rate ANOVA is exploratory and weights days equally regardless of impressions.

## Regression checks

```bash
python -m unittest discover -s tests -v
```

Tests cover weighted aggregation, empty/zero-impression inputs, invalid counts, multiple-comparison adjustment, and independent pre/post calculations. No private campaign data is needed.
