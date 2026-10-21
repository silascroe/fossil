import copy
import json
import tempfile
import subprocess
import sys
import unittest
import zipfile
from pathlib import Path
from fossil.acquire import AcquisitionError
from fossil.case import investigate, replay
from fossil.compare import compare
from fossil.inventory import inspect
from fossil.assessment import assess
from test_core import CODE


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.addCleanup(self.tmp.cleanup)
        self.a,self.b=self.root/'a',self.root/'b';self.a.mkdir();self.b.mkdir()
        for p in (self.a,self.b):(p/'module.py').write_text(CODE)

    def test_instructional_example_is_not_a_target_attribution(self):
        (self.a/'README.md').write_text('Example: create a fork of https://github.com/other/repo.\n')
        a,b=inspect(self.a),inspect(self.b)
        r=assess(compare(a,b),{'inventory':a,'git':{},'metadata':{}},{'repository':'other/repo','git':{}})
        self.assertEqual(r['verdict'],'code_overlap')

    def test_readme_component_attribution_preserves_component_scope(self):
        (self.a/'README.md').write_text('Only the optional adapter is derived from https://github.com/other/repo.\n')
        a,b=inspect(self.a),inspect(self.b)
        r=assess(compare(a,b),{'inventory':a,'git':{},'metadata':{}},{'repository':'other/repo','git':{}})
        self.assertEqual(r['verdict'],'corroborated_component')
        self.assertEqual(r['scope'],'component')

    def test_replay_rebuilds_documentary_evidence_and_checks_method_parameters(self):
        path=self.root/'case';c=investigate(str(self.a),[str(self.b)],path)
        original=copy.deepcopy(c)
        c['target']['inventory']['references']=[{'repository':'other/repo','path':'README.md','line':1,'text':'A fork of https://github.com/other/repo','statement':'A fork of https://github.com/other/repo'}]
        c['comparisons'][0]['candidate']['repository']='other/repo'
        forged=assess(compare(inspect(path/'snapshots/target'),inspect(path/'snapshots/candidate-1')),c['target'],c['comparisons'][0]['candidate'])
        c['comparisons'][0].update(forged)
        (path/'case.json').write_text(json.dumps(c))
        with self.assertRaisesRegex(AcquisitionError,'inventory|Replay mismatch'):replay(path)
        original['parameters']['min_match_tokens']=1
        (path/'case.json').write_text(json.dumps(original))
        with self.assertRaisesRegex(AcquisitionError,'parameter|method'):replay(path)

    def test_generic_zip_keeps_vendor_scope(self):
        archives=[]
        for name in ['a','b']:
            z=self.root/(name+'.zip')
            with zipfile.ZipFile(z,'w') as f:f.writestr('vendor/lib.py',CODE)
            archives.append(str(z))
        c=investigate(archives[0],[archives[1]],self.root/'case')
        self.assertEqual(c['comparisons'][0]['verdict'],'component_overlap')

    def test_repetitive_comparison_is_bounded_and_records_skipped_work(self):
        repeated=('def repetitive(alpha, beta, gamma, delta, epsilon, zeta, eta, theta, iota, kappa, lamda, mu, nu, xi, omicron, pi):\n'
                  '    temporary = alpha + beta + gamma + delta + epsilon + zeta + eta + theta\n'
                  '    return temporary + iota + kappa + lamda + mu + nu + xi + omicron + pi\n')*400
        (self.a/'module.py').write_text(repeated);(self.b/'module.py').write_text('inserted\n'+repeated)
        command = [sys.executable, '-c', 'import json,sys;from pathlib import Path;from fossil.inventory import inspect;from fossil.compare import compare;print(json.dumps(compare(inspect(Path(sys.argv[1])),inspect(Path(sys.argv[2])))))', str(self.a), str(self.b)]
        output = subprocess.run(command,capture_output=True,text=True,timeout=4,check=True)
        r=json.loads(output.stdout)
        self.assertTrue(r['skipped_pairs'])
        self.assertIn('work budget',r['skipped_pairs'][0]['reason'])


if __name__=='__main__':unittest.main()
