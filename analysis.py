"""Reusable campaign summaries and pairwise CTR comparisons."""

from itertools import combinations

import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint, proportions_ztest


def campaign_summary(data):
    """Aggregate valid binomial counts, excluding zero-impression campaigns."""
    columns = ['campaign_name', 'clicks_to_landing_page', 'impressions']
    missing = set(columns) - set(data.columns)
    if missing:
        raise ValueError(f"Missing report columns: {', '.join(sorted(missing))}")
    frame = data[columns].copy()
    if frame['campaign_name'].isna().any():
        raise ValueError('Campaign names cannot be missing.')
    counts = frame[columns[1:]].apply(pd.to_numeric, errors='raise')
    values = counts.to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values < 0).any() or (values % 1 != 0).any():
        raise ValueError('Clicks and impressions must be finite, nonnegative whole numbers.')
    if (counts['clicks_to_landing_page'] > counts['impressions']).any():
        raise ValueError('Clicks cannot exceed impressions for a binomial CTR comparison.')
    frame[columns[1:]] = counts
    summary = frame.groupby('campaign_name').agg(
        clicks=('clicks_to_landing_page', 'sum'), impressions=('impressions', 'sum')
    )
    summary = summary.loc[summary['impressions'] > 0].copy()
    summary['ctr'] = summary['clicks'] / summary['impressions']
    if summary.empty:
        summary['ci_lower'] = pd.Series(dtype=float)
        summary['ci_upper'] = pd.Series(dtype=float)
    else:
        summary['ci_lower'], summary['ci_upper'] = proportion_confint(
            summary['clicks'], summary['impressions'], method='wilson'
        )
    return summary.sort_values('ctr', ascending=False)


def pairwise_comparisons(data):
    """Compare campaigns within this data subset, applying Holm correction."""
    summary = campaign_summary(data)
    rows = []
    for first, second in combinations(summary.index, 2):
        counts = summary.loc[[first, second], 'clicks'].to_numpy(dtype=float)
        observations = summary.loc[[first, second], 'impressions'].to_numpy(dtype=float)
        if counts.sum() == 0 or counts.sum() == observations.sum():
            z_stat, p_value = 0.0, 1.0
        else:
            z_stat, p_value = proportions_ztest(counts, observations)
        rows.append({
            'Campaign 1': first, 'Campaign 2': second,
            'CTR 1': counts[0] / observations[0],
            'CTR 2': counts[1] / observations[1],
            'z-stat': z_stat, 'p-value': p_value
        })
    result = pd.DataFrame(rows, columns=[
        'Campaign 1', 'Campaign 2', 'CTR 1', 'CTR 2', 'z-stat', 'p-value'
    ])
    if result.empty:
        result['Adjusted p-value'] = pd.Series(dtype=float)
        result['Significant (Holm)'] = pd.Series(dtype=bool)
    else:
        significant, adjusted, _, _ = multipletests(result['p-value'], method='holm')
        result['Adjusted p-value'] = adjusted
        result['Significant (Holm)'] = significant
    return result
