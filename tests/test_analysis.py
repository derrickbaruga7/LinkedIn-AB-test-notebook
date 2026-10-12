import unittest

import pandas as pd

from analysis import campaign_summary, pairwise_comparisons


def report(rows):
    return pd.DataFrame(rows, columns=['campaign_name', 'clicks_to_landing_page', 'impressions'])


class CampaignAnalysisTests(unittest.TestCase):
    def test_summary_aggregates_counts_before_computing_ctr(self):
        summary = campaign_summary(report([('A', 2, 10), ('A', 8, 90), ('B', 0, 0)]))
        self.assertEqual(summary.index.tolist(), ['A'])
        self.assertAlmostEqual(summary.loc['A', 'ctr'], 0.1)
        self.assertLess(summary.loc['A', 'ci_lower'], 0.1)
        self.assertGreater(summary.loc['A', 'ci_upper'], 0.1)

    def test_three_campaigns_have_three_adjusted_comparisons(self):
        result = pairwise_comparisons(report([('A', 10, 100), ('B', 30, 100), ('C', 60, 100)]))
        self.assertEqual(len(result), 3)
        self.assertTrue((result['Adjusted p-value'] >= result['p-value']).all())

    def test_periods_use_their_own_observations(self):
        before = pairwise_comparisons(report([('A', 10, 100), ('B', 50, 100)]))
        after = pairwise_comparisons(report([('A', 90, 100), ('B', 50, 100)]))
        self.assertEqual(before.iloc[0]['Campaign 1'], 'B')
        self.assertEqual(after.iloc[0]['Campaign 1'], 'A')

    def test_identical_boundary_rates_have_no_significance(self):
        for count in [0, 100]:
            result = pairwise_comparisons(report([('A', count, 100), ('B', count, 100)]))
            self.assertEqual(result.iloc[0]['p-value'], 1)
            self.assertFalse(result.iloc[0]['Significant (Holm)'])

    def test_empty_and_single_campaign_have_no_pairs(self):
        self.assertTrue(pairwise_comparisons(report([])).empty)
        self.assertTrue(pairwise_comparisons(report([('A', 3, 10)])).empty)

    def test_invalid_counts_are_rejected(self):
        for clicks, impressions in [(11, 10), (-1, 10), (1.5, 10), (1, float('nan'))]:
            with self.assertRaises(ValueError):
                campaign_summary(report([('A', clicks, impressions)]))


if __name__ == '__main__':
    unittest.main()
