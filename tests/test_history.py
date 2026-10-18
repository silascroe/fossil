import subprocess
import tempfile
import unittest
from pathlib import Path
from fossil.acquire import AcquisitionError, history
from fossil.inventory import inspect
from fossil.compare import compare
from fossil.assessment import assess


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name); self.addCleanup(self.tmp.cleanup)

    def test_pinned_repository_input_preserves_full_ref_and_rejects_flags(self):
        from fossil.github import split_repository
        self.assertEqual(split_repository('https://github.com/althonos/pronto@3384010dfb4fc7c66a219f59276adef3288a886b'), ('althonos/pronto', '3384010dfb4fc7c66a219f59276adef3288a886b'))
        self.assertEqual(split_repository('owner/repo@release/v1'), ('owner/repo', 'release/v1'))
        with self.assertRaises(AcquisitionError): split_repository('owner/repo@--upload-pack=evil')

    def test_history_can_observe_an_old_revision_without_changing_worktree(self):
        p=self.root/'repo'; p.mkdir()
        def run(*args):
            return subprocess.check_output(['git','-C',str(p),*args],text=True).strip()
        run('init','-q'); (p/'a.py').write_text('one'); run('add','.')
        run('-c','user.name=Test','-c','user.email=t@example.invalid','commit','-qm','first')
        first=run('rev-parse','HEAD')
        (p/'a.py').write_text('two'); run('add','.')
        run('-c','user.name=Test','-c','user.email=t@example.invalid','commit','-qm','second')
        observed=history(p, first)
        self.assertEqual(observed['head'],first)
        self.assertEqual(len(observed['commits']),1)
        self.assertEqual((p/'a.py').read_text(),'two')

    def test_multiline_source_attribution_attaches_to_its_component(self):
        p=self.root/'repo'; p.mkdir()
        (p/'queues.py').write_text('"""\nThe code is derived from\nhttps://github.com/upstream/queue/commit/'+'a'*40+'\n"""\n')
        inv=inspect(p)
        self.assertIn('derived from',inv['references'][0]['statement'])
        self.assertEqual(inv['references'][0]['ref'],'a'*40)

    def test_fork_system_call_in_changelog_is_not_ancestry(self):
        p=self.root/'repo'; p.mkdir()
        (p/'CHANGELOG.md').write_text('Close database before fork [issue](https://github.com/other/repo/pull/80)\n')
        inv=inspect(p)
        result=assess(compare(inv,inv),{'inventory':inv,'metadata':{},'git':{}},{'repository':'other/repo','git':{}})
        self.assertEqual(result['verdict'],'not_established')

    def test_source_attribution_is_component_scope_even_if_application_path(self):
        from test_core import CODE
        a,b=self.root/'a',self.root/'b'; a.mkdir(); b.mkdir()
        (a/'queues.py').write_text('"""Derived from https://github.com/other/repo"""\n'+CODE)
        (b/'queues.py').write_text(CODE)
        ia,ib=inspect(a),inspect(b)
        r=assess(compare(ia,ib),{'inventory':ia,'metadata':{},'git':{}},{'repository':'other/repo','git':{}})
        self.assertEqual(r['verdict'],'corroborated_component')
        self.assertEqual(r['scope'],'component')


if __name__=='__main__': unittest.main()
