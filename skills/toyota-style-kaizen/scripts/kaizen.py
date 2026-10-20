#!/usr/bin/env python3
"""TOYOTA-style KAIZEN (unofficial) local organization ledger, Python 3.10+.

No network, model calls, arbitrary shell commands, or background execution.
Events are the source of truth. JSON summaries / Markdown memory are projections.
The hash chain detects accidental alteration, not deliberate tampering.
"""
from __future__ import annotations
import argparse
import contextlib
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

VERSION = '1.0.0'
KINDS = ('observation', 'decision', 'lesson', 'risk')
VALID_RISKS = ('low', 'medium', 'high')
MAX_NOTE = 4000
SKIP_DIRS = {'.git', '.kaizen', 'node_modules', '.venv', 'venv', 'dist', 'build', '__pycache__', '.next', 'vendor', 'target'}

class KaizenError(Exception):
    pass

def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def dump(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def ensure_local_child(path: Path):
    if path.parent.is_symlink():
        raise KaizenError(f'refusing generated file in symlinked directory: {path.parent}')

def atomic_text(path: Path, content: str):
    ensure_local_child(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.'+path.name+'-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content); f.flush(); os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp): os.unlink(temp)

def atomic_json(path: Path, value):
    ensure_local_child(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name + '-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(value, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write('\n')
            f.flush(); os.fsync(f.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

def safe_text(value: str, label: str, maxlen=MAX_NOTE):
    if not isinstance(value, str) or not value.strip() or len(value) > maxlen:
        raise KaizenError(f'{label}: 1..{maxlen} characters required')
    return value.strip()

def workspace_root(raw: str) -> Path:
    p = Path(raw).expanduser().resolve()
    if not p.is_dir():
        raise KaizenError(f'workspace directory not found: {p}')
    state = p / '.kaizen'
    if state.is_symlink():
        raise KaizenError('refusing symlink .kaizen directory')
    return p

def location(ws: Path) -> Path:
    return ws / '.kaizen'

def need_initialized(ws: Path):
    if not (location(ws) / 'charter.json').is_file() or not (location(ws) / 'events.jsonl').is_file():
        raise KaizenError('not initialized; first run init --workspace PATH')

def read_charter(ws: Path):
    need_initialized(ws)
    c = json.loads((location(ws) / 'charter.json').read_text(encoding='utf-8'))
    if not isinstance(c, dict) or not isinstance(c.get('max_active_tasks'), int) or not 1 <= c['max_active_tasks'] <= 12:
        raise KaizenError('charter.json invalid: max_active_tasks must be 1..12')
    return c

@contextlib.contextmanager
def lock(ws: Path):
    path = location(ws) / '.write.lock'
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise KaizenError('workspace is locked by another command or an interrupted run; inspect .kaizen/.write.lock before removing')
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(f'pid={os.getpid()} utc={now()}\n')
        yield
    finally:
        try: path.unlink()
        except FileNotFoundError: pass

def events_read(ws: Path):
    need_initialized(ws)
    events = []
    previous = 'GENESIS'
    for line_no, raw in enumerate((location(ws) / 'events.jsonl').read_text(encoding='utf-8').splitlines(), 1):
        if not raw.strip():
            raise KaizenError(f'blank journal line {line_no}')
        try: ev = json.loads(raw)
        except ValueError as e: raise KaizenError(f'corrupt journal line {line_no}: {e}') from e
        digest = ev.get('hash')
        body = {k:v for k,v in ev.items() if k != 'hash'}
        candidate = hashlib.sha256(dump(body).encode('utf-8')).hexdigest()
        if digest != candidate or ev.get('prev_hash') != previous or ev.get('seq') != line_no:
            raise KaizenError(f'journal integrity failure at line {line_no}; do not write until investigated')
        events.append(ev)
        previous = digest
    return events

def state_from(events):
    state = {'started': False, 'tasks': {}, 'improvements': {}, 'notes': [], 'measurements': [], 'approvals': [], 'events': len(events)}
    for ev in events:
        d = ev.get('data', {})
        k = ev.get('kind')
        if k == 'ORG_STARTED':
            state['started'] = True
            boot=d.get('initial_task')
            if boot:
                state['tasks'][boot['id']]={'id':boot['id'],'title':boot['title'],'description':boot['description'],'acceptance':boot['acceptance'],'risk':boot['risk'],'depends_on':[], 'assignee':boot['assignee'], 'status':'active','created_at':ev['at'],'started_at':ev['at'],'finished_at':None,'result':None,'evidence':[]}
        elif k == 'TASK_CREATED':
            state['tasks'][d['id']] = {'id':d['id'], 'title':d['title'], 'description':d.get('description',''), 'acceptance':d.get('acceptance',''), 'risk':d['risk'], 'depends_on':d.get('depends_on', []), 'assignee':d.get('assignee','unassigned'), 'status':'todo', 'created_at':ev['at'], 'started_at':None, 'finished_at':None, 'result':None, 'evidence':[]}
        elif k == 'TASK_STARTED':
            t = state['tasks'][d['id']]; t['status']='active'; t['started_at']=ev['at']
        elif k == 'TASK_SUBMITTED':
            t = state['tasks'][d['id']]; t['status']='review';t['result']=d['result'];t['evidence']=d['evidence']
        elif k == 'TASK_REVIEWED':
            t = state['tasks'][d['id']]; t['status']='done' if d['decision']=='accept' else 'todo'
            if d['decision']=='accept': t['finished_at']=ev['at']
        elif k == 'TASK_BLOCKED':
            state['tasks'][d['id']]['status']='blocked'
        elif k == 'APPROVAL':
            state['approvals'].append({'task':d['id'],'decision':d['decision'],'reason':d['reason'],'at':ev['at'], 'actor':d.get('actor','self-declared CEO')})
        elif k == 'MEASUREMENT':
            state.setdefault('measurements', []).append({'metric':d['metric'],'value':d['value'],'unit':d['unit'],'window':d['window'],'sample_size':d['sample_size'],'source':d['source'],'method':d['method'],'context':d['context'],'task':d.get('task'),'at':ev['at']})
        elif k == 'MEMO':
            state['notes'].append({'kind':d['category'],'text':d['text'],'task':d.get('task'), 'at':ev['at']})
        elif k == 'IMPROVEMENT_PROPOSED':
            state['improvements'][d['id']]={'id':d['id'],'hypothesis':d['hypothesis'],'risk':d['risk'],'status':'proposed','reason':None}
        elif k == 'IMPROVEMENT_DECIDED':
            state['improvements'][d['id']]['status']=d['decision'];state['improvements'][d['id']]['reason']=d['reason']
    return state

def append(ws:Path, kind:str, data:dict, expected_count=None):
    with lock(ws):
        old=events_read(ws)
        if expected_count is not None and len(old)!=expected_count:
            raise KaizenError('state changed concurrently; reload status and retry')
        ev={'seq':len(old)+1,'at':now(),'kind':kind,'data':data,'prev_hash':old[-1]['hash'] if old else 'GENESIS'}
        ev['hash']=hashlib.sha256(dump(ev).encode('utf-8')).hexdigest()
        with (location(ws)/'events.jsonl').open('a', encoding='utf-8', newline='\n') as f:
            f.write(dump(ev)+'\n'); f.flush(); os.fsync(f.fileno())
        snapshot=state_from(old+[ev])
        projections(ws,snapshot)
    return ev, snapshot

def projections(ws, state):
    s=location(ws)
    atomic_json(s/'board.json', {'tasks': list(state['tasks'].values()), 'improvements':list(state['improvements'].values()), 'started':state['started'], 'events':state['events'], 'note':'Generated from events.jsonl; DO NOT EDIT. A local workflow ledger, not a security boundary.'})
    for category in KINDS:
        records=[n for n in state['notes'] if n['kind']==category]
        content='# ' + category.capitalize()+'\n\n'
        content+='> Generated from the local event journal. Statements are not independently verified.\n\n'
        for n in records:
            content+=f"- {n['at']} / {n['task'] or 'general'}: {n['text'].replace(chr(10),' ')}\n"
        atomic_text(s/'memory'/f'{category}.md',content)

def task_id(tid):
    if not re.fullmatch(r'T\d{4,8}', tid):
        raise KaizenError('task ID must look like T0001')
    return tid

def get_task(state, tid):
    tid=task_id(tid)
    if tid not in state['tasks']:
        raise KaizenError(f'unknown task: {tid}')
    return state['tasks'][tid]

def checked_evidence(ws, names):
    verified=[]
    for name in names:
        p=(ws/name).resolve()
        if not p.is_relative_to(ws) or not p.is_file() or p.stat().st_size==0:
            raise KaizenError(f'evidence must be a non-empty existing file inside workspace: {name}')
        verified.append(str(p.relative_to(ws)))
    return verified

def inventory(ws):
    total=0; sample=[]; suffixes={}; skipped=0
    for parent, dirs, files in os.walk(ws,followlinks=False):
        dirs[:]=sorted(d for d in dirs if d not in SKIP_DIRS and not (Path(parent)/d).is_symlink())
        for name in sorted(files):
            if total>=2000:
                skipped+=1;continue
            p=Path(parent)/name
            if p.is_symlink() or not p.is_file():continue
            total+=1
            extension=p.suffix.lower() or '[none]'
            suffixes[extension]=suffixes.get(extension,0)+1
            if len(sample)<100: sample.append(str(p.relative_to(ws)))
    return {'observed_at':now(), 'files_count_capped_2000':total, 'skipped_due_to_cap':skipped, 'suffix_counts':suffixes, 'sample_paths':sample, 'limitations':'Only paths, types and counts; no source file content inspected or executed; excludes common generated folders.'}

def report(ws,state):
    tasks=state['tasks'].values(); counts={v:sum(t['status']==v for t in tasks) for v in ('todo','active','review','blocked','done')}
    cycles=[]
    for t in state['tasks'].values():
        if t['started_at'] and t['finished_at']:
            try: cycles.append((datetime.fromisoformat(t['finished_at'])-datetime.fromisoformat(t['started_at'])).total_seconds())
            except ValueError: pass
    return {'started':state['started'],'task_counts':counts,'total_tasks':len(state['tasks']),'cycle_time_seconds_mean':round(sum(cycles)/len(cycles),2) if cycles else None, 'cycle_time_sample_count':len(cycles), 'measurements_recorded':len(state['measurements']), 'improvements':{v:sum(x['status']==v for x in state['improvements'].values()) for v in ('proposed','approved_for_trial','rejected','promoted')},'journal_events':state['events'],'pending_review':[t['id'] for t in tasks if t['status']=='review'], 'metrics_note':'Counts of local events only, not evidence of external work quality or Toyota official score.'}

def cmd_init(a):
    ws=workspace_root(a.workspace); s=location(ws)
    if s.exists(): raise KaizenError(f'{s} already exists; refusing overwrite (use status/doctor if initialized)')
    mission=safe_text(a.mission or 'CEOによる方針の定義待ち', 'mission', 1000)
    s.mkdir(mode=0o700)
    for child in ('memory','reports','baseline','handoffs'):(s/child).mkdir()
    (s/'.gitignore').write_text('*\n!.gitignore\n',encoding='utf-8')
    charter={'schema':'kaizen-charter/v1','ceo':'human user','mission':mission,'max_active_tasks':2,'policy':{'default':'read_and_local_record_only','external_write':'ceo_approval_required','publish':'ceo_approval_required','deletion':'ceo_approval_required','spend':'ceo_approval_required','secrets':'do_not_record'},'caution':'CLI approval is self-asserted; no authentication, cost-control, or execution sandbox. Enforce approvals via host.'}
    atomic_json(s/'charter.json',charter)
    (s/'events.jsonl').touch(mode=0o600)
    (s/'OPERATING.md').write_text('# KAIZEN operating agreement\n\nCEO decides purpose, high-risk approvals and promotion. AI COO coordinates only within host permissions.\nRun `python <installed-skill>/scripts/kaizen.py status --workspace .` to resume.\nUse the CLI after each transition; do not edit `events.jsonl` or `board.json` manually.\nLocal event files are not encrypted, authenticated or automatically backed up.\n',encoding='utf-8')
    projections(ws,state_from([]))
    print(f'INITIALIZED {s}\nMission: {mission}\nNext: start --workspace {ws}')

def cmd_start(a):
    ws=workspace_root(a.workspace); charter=read_charter(ws);st=state_from(events_read(ws))
    if st['started']:raise KaizenError('organization already started; use status/next')
    snap=inventory(ws)
    baseline=location(ws)/'baseline'/'startup-inventory.json'
    atomic_json(baseline,snap)
    atomic_text(location(ws)/'handoffs'/'T0001.md','# T0001 first job\n\n1. Read `.kaizen/charter.json`, `.kaizen/baseline/startup-inventory.json`, `.kaizen/OPERATING.md`.\n2. Confirm the CEO mission; if unclear, ask for an objective before modifying user code.\n3. Inspect actual relevant project files with host-approved tools; distinguish observed facts from assumptions.\n4. Record findings: `python <skill-path>/scripts/kaizen.py memo --workspace . --category observation --task T0001 --text "..."`.\n5. Submit with an existing evidence file and request independent review; never self-certify quality.\n6. Do not deploy, publish, spend, delete or read secrets without host-enforced permission.\n')
    boot={'id':'T0001','title':'初回現地現物・経営方針と業務工程の棚卸し','description':'Read startup inventory, inspect project instructions and identify the first real CEO goal. Do not claim code was inspected by inventory alone.','acceptance':'Provide observed facts, hypotheses, one prioritized next task, risks and required CEO decisions.','risk':'low','assignee':'COO (host agent)'}
    append(ws,'ORG_STARTED',{'mission':charter['mission'],'baseline':'baseline/startup-inventory.json', 'initial_task':boot},expected_count=st['events'])
    print('STARTED / T0001 active; baseline inventory saved (read-only inspection).\nHandoff: .kaizen/handoffs/T0001.md\nNext: let host agent execute T0001, then memo / submit / review.')

def cmd_add(a):
    ws=workspace_root(a.workspace); read_charter(ws); st=state_from(events_read(ws))
    depends=[task_id(x) for x in (a.depends or [])]
    if any(x not in st['tasks'] for x in depends):raise KaizenError('depends_on task not found')
    tid=f'T{len(st["tasks"])+1:04d}'
    if tid in depends:raise KaizenError('self-dependency')
    risk=a.risk
    append(ws,'TASK_CREATED',{'id':tid,'title':safe_text(a.title,'title',200),'description':(a.description or '').strip()[:MAX_NOTE], 'acceptance':safe_text(a.acceptance,'acceptance',1000), 'risk':risk,'depends_on':depends,'assignee':(a.assignee or 'unassigned')[:100]},expected_count=st['events'])
    print(f'CREATED {tid}: {a.title}')

def cmd_approve(a):
    ws=workspace_root(a.workspace); st=state_from(events_read(ws)); t=get_task(st,a.task)
    if t['risk']!='high':raise KaizenError('approval record is required for high-risk tasks only')
    reason=safe_text(a.reason,'reason')
    append(ws,'APPROVAL',{'id':t['id'],'decision':a.decision,'reason':reason,'actor':'self-declared human CEO'},expected_count=st['events'])
    print(f'RECORDED {t["id"]} {a.decision} (not authenticated; host must enforce actual permissions)')

def cmd_task_start(a):
    ws=workspace_root(a.workspace); c=read_charter(ws);st=state_from(events_read(ws));t=get_task(st,a.task)
    if not st['started']:raise KaizenError('organization not started')
    if t['status'] not in ('todo','blocked'):raise KaizenError('task not startable: '+t['status'])
    active=sum(x['status']=='active' for x in st['tasks'].values())
    if active >= c['max_active_tasks']:raise KaizenError('WIP limit reached; complete/review an active task first')
    if any(st['tasks'][x]['status']!='done' for x in t['depends_on']):raise KaizenError('dependencies unfinished')
    if t['risk']=='high':
        relevant=[p for p in st['approvals'] if p['task']==t['id']]
        if not relevant or relevant[-1]['decision']!='allow':raise KaizenError('high-risk task has no latest CEO allow record')
    append(ws,'TASK_STARTED',{'id':t['id']},expected_count=st['events']);print(f'ACTIVE {t["id"]}')

def cmd_submit(a):
    ws=workspace_root(a.workspace);st=state_from(events_read(ws));t=get_task(st,a.task)
    if t['status']!='active':raise KaizenError('only active tasks may be submitted')
    ev=checked_evidence(ws,a.evidence or [])
    if not ev:raise KaizenError('submit requires at least one existing non-empty --evidence file')
    append(ws,'TASK_SUBMITTED',{'id':t['id'],'result':safe_text(a.result,'result'),'evidence':ev},expected_count=st['events'])
    print(f'REVIEW {t["id"]}; reviewer must inspect evidence and actual acceptance criteria')

def cmd_review(a):
    ws=workspace_root(a.workspace);st=state_from(events_read(ws));t=get_task(st,a.task)
    if t['status']!='review':raise KaizenError('task must be awaiting review')
    if t['risk']=='high' and a.reviewer!='ceo':raise KaizenError('high-risk review requires --reviewer ceo (attestation only)')
    append(ws,'TASK_REVIEWED',{'id':t['id'],'decision':a.decision,'reason':safe_text(a.reason,'reason'),'reviewer':a.reviewer},expected_count=st['events'])
    print(f'{"DONE" if a.decision=="accept" else "REWORK"} {t["id"]}; evidence review is an attestation, not automatic truth verification')

def cmd_block(a):
    ws=workspace_root(a.workspace);st=state_from(events_read(ws));t=get_task(st,a.task)
    if t['status'] not in ('todo','active'):raise KaizenError('task must be todo or active')
    append(ws,'TASK_BLOCKED',{'id':t['id'],'reason':safe_text(a.reason,'reason')},expected_count=st['events'])
    print('BLOCKED '+t['id'])

def cmd_memo(a):
    ws=workspace_root(a.workspace);need_initialized(ws); text=safe_text(a.text,'memo')
    st=state_from(events_read(ws))
    if a.task: get_task(st,a.task)
    append(ws,'MEMO',{'category':a.category,'text':text,'task':a.task},expected_count=st['events'])
    print(f'MEMO saved: {a.category}')

def cmd_improve(a):
    ws=workspace_root(a.workspace);st=state_from(events_read(ws)); iid=f'K{len(st["improvements"])+1:04d}'
    append(ws,'IMPROVEMENT_PROPOSED',{'id':iid,'hypothesis':safe_text(a.hypothesis,'hypothesis'),'risk':a.risk},expected_count=st['events'])
    print(f'PROPOSED {iid}; evidence not yet measured; no standard updated')

def cmd_decide(a):
    ws=workspace_root(a.workspace);st=state_from(events_read(ws))
    p=st['improvements'].get(a.id)
    if not p:raise KaizenError('unknown improvement '+a.id)
    if a.decision=='promoted':raise KaizenError('cannot auto-promote: tested evidence + human decision required; this CLI has no proven efficacy checker')
    if p['status']!='proposed':raise KaizenError('improvement already decided')
    append(ws,'IMPROVEMENT_DECIDED',{'id':a.id,'decision':a.decision,'reason':safe_text(a.reason,'reason')},expected_count=st['events'])
    print(f'{a.id}: {a.decision} (pilot outcome is unverified)')


def cmd_measure(a):
    ws=workspace_root(a.workspace); st=state_from(events_read(ws))
    if a.task: get_task(st,a.task)
    try: value=float(a.value)
    except ValueError: raise KaizenError('value must be numeric')
    import math
    if not math.isfinite(value): raise KaizenError('value must be finite')
    if a.sample_size < 1: raise KaizenError('sample_size must be >=1')
    source=checked_evidence(ws,[a.source])[0]
    data={'metric':safe_text(a.metric,'metric',80),'value':value,'unit':safe_text(a.unit,'unit',30),'window':safe_text(a.window,'window',120),'sample_size':a.sample_size,'source':source,'method':safe_text(a.method,'method',300),'context':safe_text(a.context,'context',300),'task':a.task}
    append(ws,'MEASUREMENT',data,expected_count=st['events'])
    print('MEASURED (self-declared values with an existing source file; claims NOT independently verified)')

def cmd_compare(a):
    ws=workspace_root(a.workspace); st=state_from(events_read(ws))
    b=[m for m in st['measurements'] if m['metric']==a.metric and m['window']==a.before]
    after=[m for m in st['measurements'] if m['metric']==a.metric and m['window']==a.after]
    if not b or not after: raise KaizenError('before/after measurement windows not found')
    old=b[-1]; new=after[-1]
    if a.before==a.after or old['method']!=new['method'] or old['unit']!=new['unit'] or old['context']!=new['context']:
        raise KaizenError('noncomparable windows, method, unit or context')
    diff=new['value']-old['value']
    good=diff>0 if a.direction=='higher' else diff<0
    result={'metric':a.metric,'before':old,'after':new,'difference':round(diff,6),'direction':a.direction,'indicated_change':'favorable' if good else 'unfavorable' if diff else 'unchanged','verification':'NOT_VERIFIED: sources are only checked for nonempty existence; no causal attribution or statistical significance established','action':'Recommend independent review and confounder checks; never auto-promote.'}
    print(json.dumps(result,ensure_ascii=False,indent=2))

def cmd_doctor(a):
    ws=workspace_root(a.workspace);c=read_charter(ws)
    ev=events_read(ws);s=state_from(ev)
    checks={'journal_hash_chain':'PASS','charter':'PASS','projection':'PASS','WIP':'PASS','tasks':'PASS'}
    expected= {'tasks':list(s['tasks'].values()), 'improvements':list(s['improvements'].values()),'started':s['started'],'events':s['events'],'note':'Generated from events.jsonl; DO NOT EDIT. A local workflow ledger, not a security boundary.'}
    board_path=location(ws)/'board.json'
    if not board_path.is_file() or json.loads(board_path.read_text(encoding='utf-8'))!=expected:checks['projection']='FAIL'
    for category in KINDS:
        if not (location(ws)/'memory'/f'{category}.md').is_file():checks['projection']='FAIL'
    if sum(t['status']=='active' for t in s['tasks'].values())>c['max_active_tasks']:checks['WIP']='FAIL'
    for t in s['tasks'].values():
        if any(dep not in s['tasks'] for dep in t['depends_on']):checks['tasks']='FAIL'
    if a.repair and checks['projection']=='FAIL':
        with lock(ws):
            # refuse overwriting newer state from another writer
            if len(events_read(ws)) != len(ev):
                raise KaizenError('journal changed during repair; retry')
            projections(ws,s)
        checks['projection']='PASS'
        print('Projection regenerated from checked event journal')
    print(json.dumps({'checks':checks, 'status':'PASS' if all(x=='PASS' for x in checks.values()) else 'FAIL','warning':'Journal hashes are not authentication or tamper-proof proof'},ensure_ascii=False,indent=2))
    return 0 if all(x=='PASS' for x in checks.values()) else 3

def cmd_report(a):
    ws=workspace_root(a.workspace); st=state_from(events_read(ws)); payload=report(ws,st)
    if a.write:
        path=location(ws)/'reports'/('status-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.json')
        atomic_json(path,payload);print(f'WROTE {path}')
    print(json.dumps(payload,ensure_ascii=False,indent=2))


def cmd_diagnose(a):
    ws=workspace_root(a.workspace); c=read_charter(ws); st=state_from(events_read(ws))
    count=report(ws,st)['task_counts']; signals=[]; strengths=[]
    blocked=[t['id'] for t in st['tasks'].values() if t['status']=='blocked']
    waiting=[t['id'] for t in st['tasks'].values() if t['status']=='todo' and any(st['tasks'].get(dep,{}).get('status')!='done' for dep in t['depends_on'])]
    if blocked: signals.append({'signal':'BLOCKED_WORK','tasks':blocked,'meaning':'A task is stopped; check cause and ownership, not blame'})
    if waiting: signals.append({'signal':'DEPENDENCY_WAIT','tasks':waiting,'meaning':'Tasks await a prior accepted artifact'})
    if count['active']>=c['max_active_tasks']: signals.append({'signal':'WIP_AT_LIMIT','tasks':[],'meaning':'WIP is at configured limit; inspect throughput before adding workers'})
    if count['review']: signals.append({'signal':'PENDING_REVIEW','tasks':[t['id'] for t in st['tasks'].values() if t['status']=='review'],'meaning':'Review queue exists, but no delay is proven until timing data is measured'})
    if count['done'] and not st['measurements']: signals.append({'signal':'MEASUREMENT_GAP','tasks':[],'meaning':'Finished work exists but no comparable performance measurements are recorded'})
    if count['done']: strengths.append({'signal':'ACCEPTED_DELIVERIES','count':count['done'],'meaning':'Task state shows accepted deliveries, not independent proof of quality'})
    if st['notes']: strengths.append({'signal':'MEMORY_ACTIVITY','count':len(st['notes']),'meaning':'Records exist, but their claims are not automatically verified'})
    print(json.dumps({'observed_at':now(),'attention_signals':signals,'recorded_positive_signals':strengths,'recommended_next':'Review the highest-impact signal with evidence; do nothing if it is not actually harmful','confidence':'Only local CLI state is observed; no agent host telemetry, quality truth, or causal inference'},ensure_ascii=False,indent=2))

def cmd_status(a):
    ws=workspace_root(a.workspace);st=state_from(events_read(ws));print(json.dumps(report(ws,st),ensure_ascii=False,indent=2))
    for t in st['tasks'].values():
        print(f"{t['id']} [{t['status']}] {t['risk']} {t['title']}")

def cmd_next(a):
    ws=workspace_root(a.workspace);s=state_from(events_read(ws));c=read_charter(ws)
    if not s['started']: print('Next: start');return
    for t in s['tasks'].values():
        if t['status']=='review':print(f"Next: review {t['id']} - {t['title']}");return
    for t in s['tasks'].values():
        if t['status']=='active':print(f"Next: work on {t['id']} - {t['title']}");return
    for t in s['tasks'].values():
        if t['status']=='todo' and all(s['tasks'][d]['status']=='done' for d in t['depends_on']):
            print(f"Next: task-start {t['id']} - {t['title']}");return
    print('No executable tasks. CEO/COO: define next task or review blocked work.')

def parser():
    p=argparse.ArgumentParser(description='TOYOTA-style KAIZEN local ledger v'+VERSION)
    p.add_argument('--version',action='version',version=VERSION)
    sub=p.add_subparsers(dest='command',required=True)
    def new(name,fn):
        x=sub.add_parser(name); x.add_argument('--workspace',default='.'); x.set_defaults(func=fn);return x
    x=new('init',cmd_init);x.add_argument('--mission')
    new('start',cmd_start)
    x=new('add',cmd_add);x.add_argument('--title',required=True);x.add_argument('--description');x.add_argument('--acceptance',required=True);x.add_argument('--risk',choices=VALID_RISKS,default='low');x.add_argument('--depends',action='append');x.add_argument('--assignee')
    x=new('task-start',cmd_task_start);x.add_argument('--task',required=True)
    x=new('approve',cmd_approve);x.add_argument('--task',required=True);x.add_argument('--decision',choices=['allow','deny'],required=True);x.add_argument('--reason',required=True)
    x=new('submit',cmd_submit);x.add_argument('--task',required=True);x.add_argument('--result',required=True);x.add_argument('--evidence',action='append')
    x=new('review',cmd_review);x.add_argument('--task',required=True);x.add_argument('--decision',choices=['accept','rework'],required=True);x.add_argument('--reason',required=True);x.add_argument('--reviewer',choices=['agent','ceo'],default='agent')
    x=new('block',cmd_block);x.add_argument('--task',required=True);x.add_argument('--reason',required=True)
    x=new('memo',cmd_memo);x.add_argument('--category',choices=KINDS,required=True);x.add_argument('--text',required=True);x.add_argument('--task')
    x=new('improve',cmd_improve);x.add_argument('--hypothesis',required=True);x.add_argument('--risk',choices=VALID_RISKS,default='medium')
    x=new('measure',cmd_measure);x.add_argument('--metric',required=True);x.add_argument('--value',required=True);x.add_argument('--unit',required=True);x.add_argument('--window',required=True);x.add_argument('--sample-size',type=int,required=True);x.add_argument('--source',required=True);x.add_argument('--method',required=True);x.add_argument('--context',required=True);x.add_argument('--task')
    x=new('compare',cmd_compare);x.add_argument('--metric',required=True);x.add_argument('--before',required=True);x.add_argument('--after',required=True);x.add_argument('--direction',choices=['higher','lower'],required=True)
    x=new('improvement-decision',cmd_decide);x.add_argument('--id',required=True);x.add_argument('--decision',choices=['approved_for_trial','rejected'],required=True);x.add_argument('--reason',required=True)
    x=new('doctor',cmd_doctor);x.add_argument('--repair',action='store_true')
    x=new('report',cmd_report);x.add_argument('--write',action='store_true')
    new('status',cmd_status);new('next',cmd_next);new('diagnose',cmd_diagnose)
    return p

def main(argv=None):
    try:
        a=parser().parse_args(argv)
        return a.func(a) or 0
    except (KaizenError, ValueError, OSError, KeyError, TypeError) as e:
        print(f'KAIZEN ERROR: {e}',file=sys.stderr)
        return 2

if __name__=='__main__':raise SystemExit(main())
