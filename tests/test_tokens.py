import tempfile
import unittest
from pathlib import Path
from fossil.inventory import inspect
from fossil.compare import compare
from test_core import CODE


class TokenTests(unittest.TestCase):
    def test_python_formatting_quote_styles_and_docstrings_do_not_hide_code(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=Path(d)/'a',Path(d)/'b';a.mkdir();b.mkdir()
            (a/'x.py').write_text(CODE)
            changed=CODE.replace('"', "'").replace('    reconstructed_strata', '    """New documentation."""\n    reconstructed_strata',1)
            (b/'x.py').write_text(changed)
            r=compare(inspect(a),inspect(b))
            self.assertEqual(r['verdict'],'code_overlap')
            self.assertEqual(r['application_token_coverage'],1.0)
            self.assertEqual(r['matches'][0]['target_lines'][0],1)
            self.assertEqual(r['matches'][0]['candidate_lines'][0],1)

    def test_reference_negation_does_not_turn_overlap_into_derivation(self):
        from fossil.assessment import assess
        with tempfile.TemporaryDirectory() as d:
            a,b=Path(d)/'a',Path(d)/'b';a.mkdir();b.mkdir()
            (a/'x.py').write_text(CODE);(b/'x.py').write_text(CODE)
            (a/'README.md').write_text('This is not a fork of https://github.com/other/repo\n')
            ia,ib=inspect(a),inspect(b)
            r=assess(compare(ia,ib),{'inventory':ia,'git':{},'metadata':{}},{'repository':'other/repo','git':{}})
            self.assertEqual(r['verdict'],'code_overlap')
            self.assertEqual(r['documentary'],[])


if __name__=='__main__':unittest.main()
