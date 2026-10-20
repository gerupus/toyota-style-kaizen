#!/usr/bin/env python3
"""Opt-in project installation. Copies one portable skill and optionally boots local state."""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / 'skills' / 'toyota-style-kaizen'

def main():
    p=argparse.ArgumentParser(description='Install TOYOTA-style KAIZEN Agent Skill (unofficial)')
    p.add_argument('--target',required=True,help='An EXISTING project directory')
    p.add_argument('--agent',choices=('codex','claude','both'),required=True)
    p.add_argument('--init',action='store_true',help='Create .kaizen/ local state; never overwrite')
    p.add_argument('--start',action='store_true',help='Start first read-only onboarding task; requires --init')
    p.add_argument('--mission',help='CEO mission; stored locally. Do NOT pass secrets here')
    p.add_argument('--write-agent-guide',action='store_true',help='Opt in to creating AGENTS.md / CLAUDE.md only when absent')
    a=p.parse_args()
    target=Path(a.target).expanduser().resolve()
    if not target.is_dir():p.error('target is not an existing directory')
    if a.start and not a.init:p.error('--start requires --init')
    if a.mission and not a.init:p.error('--mission requires --init')
    if (target/'.kaizen').exists() and a.init:p.error('target already contains .kaizen; refusing to overwrite')
    agents=['codex','claude'] if a.agent=='both' else [a.agent]
    paths=[target / ('.agents' if x=='codex' else '.claude') / 'skills' / 'toyota-style-kaizen' for x in agents]
    for path in paths:
        if path.exists() or path.is_symlink():p.error(f'already installed at {path}; refusing overwrite')
    guide_paths=[target / ('AGENTS.md' if x=='codex' else 'CLAUDE.md') for x in agents] if a.write_agent_guide else []
    for path in guide_paths:
        if path.exists() or path.is_symlink():p.error(f'{path} exists; will not replace project instructions')
    print('Installing Agent Skill only; no AI calls or external operations.')
    installed=[]
    try:
        for path in paths:
            path.parent.mkdir(parents=True,exist_ok=True)
            with tempfile.TemporaryDirectory(prefix='kaizen-install-',dir=path.parent) as tmp:
                staging=Path(tmp)/'toyota-style-kaizen'
                shutil.copytree(SOURCE,staging,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
                staging.rename(path)
            installed.append(path)
            print('INSTALLED',path)
        for agent, path in zip(agents, guide_paths):
            skill_path=('.agents' if agent=='codex' else '.claude')+'/skills/toyota-style-kaizen'
            text=('# TOYOTA-style KAIZEN (unofficial) - project opt-in\n\n'
                  'For CEO-directed task planning, work coordination, process improvement and retrospectives, read `'+skill_path+'/SKILL.md`.\n'
                  'Before work, run `python '+skill_path+'/scripts/kaizen.py doctor --workspace .` then `status` and `next` to resume existing state.\n'
                  'After observing, deciding or learning, record factual memos with this CLI; track task states and attach actual evidence before review.\n'
                  'No automatic API calls, no invented telemetry, no self-approval of restricted actions and no secrets in the journal.\n'
                  'The human CEO and hosting runtime retain real approval and tool control. Do not initialize automatically over existing state.\n')
            path.write_text(text,encoding='utf-8')
            print('PROJECT GUIDE',path)
        if a.init:
            script=paths[0]/'scripts'/'kaizen.py'
            args=[sys.executable,str(script),'init','--workspace',str(target)]
            if a.mission:args+=['--mission',a.mission]
            subprocess.run(args,check=True)
            if a.start:subprocess.run([sys.executable,str(script),'start','--workspace',str(target)],check=True)
    except Exception:
        print('Installation interrupted. Created files are not deleted automatically; inspect target paths before retrying.',file=sys.stderr)
        raise
    print('READY. In your agent, request: Read toyota-style-kaizen and continue KAIZEN T0001.')
    if not a.init: print('For local recordkeeping: run the installed skill script: init --workspace TARGET then start --workspace TARGET')

if __name__=='__main__':main()
