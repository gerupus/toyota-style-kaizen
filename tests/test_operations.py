import importlib.util
import json
import io
import contextlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
CLI=ROOT/'skills/toyota-style-kaizen/scripts/kaizen.py'
INSTALLER=ROOT/'scripts/install.py'
spec=importlib.util.spec_from_file_location('kaizen_cli', CLI)
kaizen_cli=importlib.util.module_from_spec(spec)
spec.loader.exec_module(kaizen_cli)

class LocalWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.ws=Path(self.tmp.name)/'project';self.ws.mkdir()
        (self.ws/'hello.py').write_text('print("hi")\n')
    def run_cli(self,*args,ok=True):
        stdout=io.StringIO(); stderr=io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code=kaizen_cli.main([*args,'--workspace',str(self.ws)])
            except SystemExit as exc:
                code=exc.code if isinstance(exc.code,int) else 2
        self.assertEqual(code==0,ok,msg=stdout.getvalue()+stderr.getvalue())
        return type('CLIResult',(),{'stdout':stdout.getvalue(),'stderr':stderr.getvalue(),'returncode':code})()
    def bootstrap(self):
        self.run_cli('init','--mission','Safely improve docs')
        self.run_cli('start')
    def data(self):
        return json.loads((self.ws/'.kaizen/board.json').read_text())
    def test_init_creates_local_file_memory_and_rejects_second_init(self):
        self.run_cli('init','--mission','test')
        self.assertTrue((self.ws/'.kaizen/memory/lesson.md').exists())
        self.assertTrue((self.ws/'.kaizen/memory/observation.md').exists())
        self.assertTrue((self.ws/'.kaizen/.gitignore').exists())
        self.run_cli('init',ok=False)
        self.assertEqual((self.ws/'hello.py').read_text(),'print("hi")\n')
    def test_start_readonly_inventory_task_and_recovery(self):
        self.bootstrap()
        board=self.data();self.assertTrue(board['started'])
        self.assertEqual(board['events'],1)
        self.assertEqual(board['tasks'][0]['status'],'active')
        self.assertTrue((self.ws/'.kaizen/handoffs/T0001.md').exists())
        self.assertTrue((self.ws/'.kaizen/baseline/startup-inventory.json').exists())
        self.assertEqual((self.ws/'hello.py').read_text(),'print("hi")\n')
        self.run_cli('start',ok=False)
        self.run_cli('doctor')
    def test_status_restart_persists_memo(self):
        self.bootstrap()
        self.run_cli('memo','--category','lesson','--task','T0001','--text','Reviewed the real inventory')
        self.assertIn('Reviewed the real inventory',(self.ws/'.kaizen/memory/lesson.md').read_text())
        self.assertIn('journal_events',self.run_cli('status').stdout)
        self.run_cli('doctor')
    def test_dag_wip_and_review(self):
        self.bootstrap()
        self.run_cli('add','--title','First change','--acceptance','Record test data')
        self.run_cli('add','--title','Depends on second','--acceptance','Pass check','--depends','T0002')
        self.run_cli('task-start','--task','T0003',ok=False)
        self.run_cli('task-start','--task','T0002')
        self.run_cli('submit','--task','T0002','--result','done','--evidence','missing.txt',ok=False)
        (self.ws/'evidence.md').write_text('Evidence exists; reviewer checks validity')
        self.run_cli('submit','--task','T0002','--result','done','--evidence','evidence.md')
        self.run_cli('review','--task','T0002','--decision','accept','--reason','checked the evidence file')
        self.run_cli('task-start','--task','T0003')
        self.assertEqual(len([t for t in self.data()['tasks'] if t['status']=='active']),2)
        self.run_cli('doctor')
    def test_high_risk_requires_ceo_attestation_but_not_auth(self):
        self.bootstrap()
        self.run_cli('add','--title','High risk','--risk','high','--acceptance','CEO check')
        self.run_cli('task-start','--task','T0002',ok=False)
        self.run_cli('approve','--task','T0002','--decision','allow','--reason','CEO agrees in external host')
        self.run_cli('task-start','--task','T0002')
        (self.ws/'check.txt').write_text('Some actual evidence')
        self.run_cli('submit','--task','T0002','--result','needs review','--evidence','check.txt')
        self.run_cli('review','--task','T0002','--decision','accept','--reason','check','--reviewer','agent',ok=False)
        self.run_cli('review','--task','T0002','--decision','accept','--reason','check','--reviewer','ceo')
    def test_evidence_must_be_nonempty_existing_and_inside_workspace(self):
        self.bootstrap()
        (self.ws/'empty.txt').touch()
        self.run_cli('submit','--task','T0001','--result','done','--evidence','empty.txt',ok=False)
        (Path(self.tmp.name)/'outside.txt').write_text('outside')
        self.run_cli('submit','--task','T0001','--result','done','--evidence','../outside.txt',ok=False)
        self.assertEqual(self.data()['tasks'][0]['status'],'active')
    def test_blocked_task_can_restart(self):
        self.bootstrap()
        self.run_cli('block','--task','T0001','--reason','read-only tool missing')
        self.run_cli('task-start','--task','T0001')
        self.run_cli('doctor')
    def test_journal_corruption_is_fail_closed(self):
        self.bootstrap()
        journal=self.ws/'.kaizen/events.jsonl'
        journal.write_text(journal.read_text().replace('T0001','T9999'))
        self.run_cli('doctor',ok=False)
        self.run_cli('memo','--category','lesson','--text','should reject',ok=False)
    def test_projection_can_be_repaired_from_good_journal(self):
        self.bootstrap()
        (self.ws/'.kaizen/board.json').write_text('{}')
        self.run_cli('doctor',ok=False)
        self.run_cli('doctor','--repair')
        self.run_cli('doctor')
    def test_measure_comparison_requires_real_files_and_matching_method(self):
        self.bootstrap()
        (self.ws/'before.txt').write_text('Actual recorded baseline')
        (self.ws/'after.txt').write_text('Actual recorded trial')
        self.run_cli('measure','--metric','seconds','--value','10','--unit','s','--window','baseline','--sample-size','3','--source','before.txt','--method','timer','--context','same job')
        self.run_cli('measure','--metric','seconds','--value','9','--unit','s','--window','trial','--sample-size','3','--source','after.txt','--method','timer','--context','same job')
        result=self.run_cli('compare','--metric','seconds','--before','baseline','--after','trial','--direction','lower')
        self.assertIn('NOT_VERIFIED',result.stdout)
        self.assertIn('favorable',result.stdout)
        self.run_cli('compare','--metric','seconds','--before','trial','--after','trial','--direction','lower',ok=False)
        self.run_cli('measure','--metric','seconds','--value','nan','--unit','s','--window','bad','--sample-size','3','--source','before.txt','--method','timer','--context','same job',ok=False)
    def test_no_auto_promotion_even_good_improvement(self):
        self.bootstrap()
        self.run_cli('improve','--hypothesis','Fewer reviews reduce time')
        self.run_cli('improvement-decision','--id','K0001','--decision','approved_for_trial','--reason','limited test')
        self.run_cli('improvement-decision','--id','K0001','--decision','promoted','--reason','no evidence',ok=False)
        self.assertEqual(self.data()['improvements'][0]['status'],'approved_for_trial')
    def test_stale_lock_denies_writes(self):
        self.bootstrap()
        (self.ws/'.kaizen/.write.lock').write_text('Other live process')
        self.run_cli('memo','--category','risk','--text','concurrent',ok=False)
    def test_missing_memory_detected_and_repaired(self):
        self.bootstrap()
        (self.ws/'.kaizen/memory/risk.md').unlink()
        self.run_cli('doctor',ok=False)
        self.run_cli('doctor','--repair')
        self.assertTrue((self.ws/'.kaizen/memory/risk.md').exists())
    def test_wip_limit_third_task_rejected(self):
        self.bootstrap()
        self.run_cli('add','--title','Task 2','--acceptance','Evidence required')
        self.run_cli('add','--title','Task 3','--acceptance','Evidence required')
        self.run_cli('task-start','--task','T0002')
        self.run_cli('task-start','--task','T0003',ok=False)
    def test_review_rework_and_reenter(self):
        self.bootstrap()
        (self.ws/'actual.md').write_text('Actual report')
        self.run_cli('submit','--task','T0001','--result','initial','--evidence','actual.md')
        self.run_cli('review','--task','T0001','--decision','rework','--reason','needs proof')
        self.assertEqual(self.data()['tasks'][0]['status'],'todo')
        self.run_cli('task-start','--task','T0001')
        self.run_cli('submit','--task','T0001','--result','revised','--evidence','actual.md')
        self.run_cli('review','--task','T0001','--decision','accept','--reason','verified')
        self.assertEqual(self.data()['tasks'][0]['status'],'done')
    def test_local_memory_symlink_refused(self):
        if sys.platform=='win32':self.skipTest('Symlink privilege differs on Windows')
        self.run_cli('init','--mission','test')
        from shutil import rmtree
        rmtree(self.ws/'.kaizen/memory')
        external=Path(self.tmp.name)/'external'
        external.mkdir()
        (self.ws/'.kaizen/memory').symlink_to(external,target_is_directory=True)
        self.run_cli('memo','--category','risk','--text','should not escape',ok=False)
        self.assertEqual(list(external.iterdir()),[])

    def test_diagnose_detects_positive_and_negative_signals_without_fake_score(self):
        self.bootstrap()
        self.run_cli('memo','--category','observation','--task','T0001','--text','Real inventory exists')
        self.run_cli('add','--title','Blocked downstream','--acceptance','Output required','--depends','T0001')
        out=self.run_cli('diagnose')
        self.assertIn('DEPENDENCY_WAIT',out.stdout)
        self.assertIn('MEMORY_ACTIVITY',out.stdout)
        self.assertNotIn('organization_index',out.stdout)
        self.assertIn('no agent host telemetry',out.stdout)

    def test_install_refuses_to_overwrite_existing_agent_instructions(self):
        guide=self.ws/'AGENTS.md'
        guide.write_text('Existing instructions\n')
        done=subprocess.run([sys.executable,str(INSTALLER),'--target',str(self.ws),'--agent','codex','--write-agent-guide','--init'],capture_output=True,text=True)
        self.assertNotEqual(done.returncode,0)
        self.assertEqual(guide.read_text(),'Existing instructions\n')
        self.assertFalse((self.ws/'.agents').exists())
        self.assertFalse((self.ws/'.kaizen').exists())

    def test_install_both_self_contained_and_start(self):
        cmd=[sys.executable,str(INSTALLER),'--target',str(self.ws),'--agent','both','--write-agent-guide','--init','--start','--mission','Improve demo']
        done=subprocess.run(cmd,capture_output=True,text=True)
        self.assertEqual(done.returncode,0,done.stderr+done.stdout)
        self.assertTrue((self.ws/'.claude/skills/toyota-style-kaizen/scripts/kaizen.py').exists())
        self.assertTrue((self.ws/'.agents/skills/toyota-style-kaizen/references/OPERATIONS.md').exists())
        self.assertIn('record factual memos',(self.ws/'AGENTS.md').read_text())
        self.assertIn('record factual memos',(self.ws/'CLAUDE.md').read_text())
        self.run_cli('doctor')
        repeated=subprocess.run(cmd,capture_output=True,text=True)
        self.assertNotEqual(repeated.returncode,0)

if __name__=='__main__':unittest.main()
