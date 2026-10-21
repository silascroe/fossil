import tempfile
import unittest
from pathlib import Path
from fossil.inventory import inspect
from fossil.assessment import assess
from fossil.compare import compare
from test_core import CODE


class BoundsTests(unittest.TestCase):
    def test_source_token_budget_is_explicit_and_replayable(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'large.py').write_text(CODE*500)
            inv=inspect(p)
            self.assertLessEqual(len(inv['files'][0]['tokens']),30000)
            self.assertTrue(any('token limit' in w.lower() for w in inv['warnings']))

    def test_same_canonical_github_repository_is_identity_not_ancestry(self):
        inv={'files':[],'dependencies':[],'references':[]}
        a={'repository':'canonical/repo','inventory':inv,'git':{},'metadata':{}}
        b={'repository':'canonical/repo','git':{}}
        r=assess(compare(inv,inv),a,b)
        self.assertEqual(r['verdict'],'same_repository')
        self.assertEqual(r['direction'],'not applicable')

    def test_discovery_provenance_is_bounded_and_keeps_strong_reasons(self):
        from fossil.discovery import find_candidates
        refs=[{'repository':'up/repo','path':'CHANGELOG.md','line':i,'text':'Issue https://github.com/up/repo'} for i in range(100)]
        refs.append({'repository':'up/repo','path':'README.md','line':1,'text':'A fork of https://github.com/up/repo'})
        class Service:
            def get(self,route):return {'items':[]}
        inv={'files':[],'references':refs,'symbols':[]}
        leads,_=find_candidates({'input':'target','metadata':{}},inv,Service())
        self.assertLessEqual(len(leads['up/repo']),8)
        self.assertTrue(any('README' in r for r in leads['up/repo']))


if __name__=='__main__':unittest.main()
