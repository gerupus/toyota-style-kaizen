from pathlib import Path
import json
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/toyota-style-kaizen'

class ReleaseIntegrityTests(unittest.TestCase):
    def test_agent_skill_entrypoint_and_bundled_paths(self):
        text=(SKILL/'SKILL.md').read_text(encoding='utf-8')
        self.assertTrue(text.startswith('---\n'))
        self.assertIn('name: toyota-style-kaizen',text)
        self.assertIn('version: "1.0.0"',text)
        self.assertTrue((SKILL/'scripts/kaizen.py').is_file())
        refs=re.findall(r'`(references/[A-Za-z0-9_.\-/]+|templates/[A-Za-z0-9_.\-/]+)`',text)
        self.assertGreaterEqual(len(refs),5)
        for ref in refs:
            self.assertTrue((SKILL/ref).is_file(),ref)
    def test_docs_and_license_present(self):
        for p in ['README.md','README.en.md','LICENSE','CONTRIBUTING.md','docs/SECURITY.md','docs/IMPLEMENTATION-STATUS.md','docs/ARCHITECTURE.md','.github/workflows/validate.yml']:
            self.assertTrue((ROOT/p).is_file(),p)
    def test_no_obsolete_private_preview_in_entrypoint(self):
        skill=(SKILL/'SKILL.md').read_text()
        self.assertNotIn('ceo-managed-agent-organization.md',skill)
        self.assertNotIn('score_org.py',skill)
    def test_template_valid_json(self):
        data=json.loads((SKILL/'templates/charter.example.json').read_text())
        self.assertEqual(data['max_active_tasks'],2)

if __name__=='__main__':unittest.main()
