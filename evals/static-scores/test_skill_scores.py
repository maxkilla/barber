import json, os, subprocess, sys, unittest
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, '..', '..', 'scripts'))
import skill_scores as ss

def fx(name): return ss.score_file(os.path.join(here, 'fixtures', name, 'SKILL.md'))

class Scores(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clean, cls.bloated, cls.mismatch = fx('clean'), fx('bloated'), fx('mismatch')

    def test_bloated_has_more_repeats(self):
        self.assertGreater(self.bloated['conciseness']['repeated_ratio'], 0.5)
        self.assertLess(self.clean['conciseness']['repeated_ratio'], 0.05)

    def test_bloated_has_more_empty_lines_and_length(self):
        self.assertGreater(self.bloated['conciseness']['empty_ratio'], self.clean['conciseness']['empty_ratio'])
        self.assertGreater(self.bloated['conciseness']['lines'], self.clean['conciseness']['lines'])

    def test_conciseness_orders_clean_above_bloated(self):
        self.assertGreater(self.clean['conciseness']['score'], self.bloated['conciseness']['score'] + 15)

    def test_consistency_orders_clean_above_mismatch(self):
        self.assertGreater(self.clean['consistency']['score'], self.mismatch['consistency']['score'] + 15)

    def test_each_consistency_metric_orders_clean_above_mismatch(self):
        for k in ('keyword_cov', 'tfidf_cos', 'title_cov'):
            self.assertGreater(self.clean['consistency'][k], self.mismatch['consistency'][k], k)

    def test_mismatch_is_still_concise(self):
        # mismatch is a consistency fault, not a bloat fault
        self.assertGreater(self.mismatch['conciseness']['score'], self.bloated['conciseness']['score'])

    def test_clean_wins_overall(self):
        tot = lambda r: r['conciseness']['score'] + r['consistency']['score']
        self.assertGreater(tot(self.clean), tot(self.bloated))
        self.assertGreater(tot(self.clean), tot(self.mismatch))

    def test_folded_description_parsed(self):
        r = ss.score_text('---\nname: x\ndescription: >\n  Cleans csv files\n  and dedupes rows\n---\n## Dedupe rows\nCleans csv.\n')
        self.assertTrue(r['description_found'])

    def test_no_frontmatter_does_not_crash(self):
        r = ss.score_text('# just a body\nsome text\n')
        self.assertFalse(r['description_found'])
        self.assertEqual(r['consistency']['score'], 0.0)

    def test_cli_json(self):
        p = os.path.join(here, 'fixtures', 'clean', 'SKILL.md')
        out = subprocess.run([sys.executable, os.path.join(here, '..', '..', 'scripts', 'skill_scores.py'), '--json', p],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0)
        self.assertIn('conciseness', json.loads(out.stdout)[0])

if __name__ == '__main__':
    unittest.main()
