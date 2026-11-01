#!/usr/bin/env python3
"""Run blind, isolated Codex behaviour trials. Requires authenticated Codex CLI.

This is an opt-in model evaluation, separate from deterministic check.py/CI.
The runner receives the skill, user prompt and attachments, never expectations.
Native tools in cases 29+ are instrumented adapters, not actual desktop UI.
Grade saved responses separately against evals.json, quoting observed evidence.
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'closebook'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True, help='New output directory for private raw logs and isolated workspaces')
    parser.add_argument('--ids', help='Comma-separated case IDs; default: all')
    parser.add_argument('--jobs', type=int, default=2)
    parser.add_argument('--model')
    parser.add_argument('--reasoning')
    parser.add_argument('--timeout', type=int, default=300)
    args = parser.parse_args()
    if args.jobs < 1 or args.jobs > 8:
        parser.error('--jobs must be between 1 and 8')
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    cases = json.loads((SKILL / 'evals/evals.json').read_text())['evals']
    if args.ids:
        wanted = {int(value) for value in args.ids.split(',')}
        cases = [case for case in cases if case['id'] in wanted]
        if {case['id'] for case in cases} != wanted:
            parser.error('Unknown eval ID')
    snapshot = out / 'skill-snapshot'
    shutil.copytree(SKILL, snapshot, ignore=shutil.ignore_patterns('evals', '__pycache__', '._*', '.DS_Store'))
    hashes = {str(path.relative_to(snapshot)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in snapshot.rglob('*') if path.is_file()}
    (out / 'source-hashes.json').write_text(json.dumps(hashes, indent=2) + '\n')
    codex = shutil.which('codex')
    if not codex:
        parser.error('Codex CLI is required')
    (out / 'run.json').write_text(json.dumps({'ids': [case['id'] for case in cases], 'model': args.model,
                                            'reasoning': args.reasoning, 'tool_mode': 'instrumented adapters; not real native UI'}, indent=2) + '\n')

    def run(case):
        case_dir = out / ('eval-%02d' % case['id'])
        workspace = case_dir / 'workspace'
        workspace.mkdir(parents=True)
        shutil.copytree(snapshot, workspace / 'closebook')
        attached = []
        for item in case['files']:
            target = workspace / 'attachments' / Path(item).name
            target.parent.mkdir(exist_ok=True)
            shutil.copy2(SKILL / item, target)
            attached.append(str(target.relative_to(workspace)))
        before = {str(path.relative_to(workspace)): hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in workspace.rglob('*') if path.is_file()}
        command = [codex, 'exec', '--ignore-user-config', '--ephemeral', '--skip-git-repo-check',
                   '--disable', 'apps', '--disable', 'plugins', '--disable', 'multi_agent',
                   '--enable', 'skip_host_skill_discovery', '--disable', 'browser_use', '--disable', 'computer_use',
                   '-c', 'approval_policy="never"', '-s', 'workspace-write',
                   '-C', str(workspace), '--json', '-o', str(case_dir / 'response.md')]
        if args.model:
            command += ['-c', 'model=' + json.dumps(args.model)]
        if args.reasoning:
            command += ['-c', 'model_reasoning_effort=' + json.dumps(args.reasoning)]
        tool_cases = {29: ['closebook_card', 'host_native'], 30: ['closebook_card', 'host_native'], 31: ['closebook_card', 'host_native'],
                      32: ['closebook_card', 'host_native'], 33: ['closebook_card', 'learning_progress'], 34: ['closebook_card', 'host_native'],
                      39: [], 40: ['closebook_card', 'host_widget'], 41: ['host_question'],
                      42: ['closebook_card', 'host_widget'], 43: [], 44: []}
        servers = tool_cases.get(case['id'], [])
        for server in servers:
            prefix = 'mcp_servers.' + server
            command += ['-c', prefix + '.command=' + json.dumps(sys.executable),
                        '-c', prefix + '.args=' + json.dumps([str(ROOT / 'tools/behavior_mcp_stub.py'), '--server', server,
                                                            '--case', str(case['id']), '--log', str(case_dir / (server + '.jsonl'))]),
                        '-c', prefix + '.required=true']
        prompt = ('Use the closebook skill at ./closebook/SKILL.md to respond to the learner below. '
                  'Read only that skill and its routed references and the provided attachments. '
                  'The bracketed environment describes the learning scenario; respect its capabilities. '
                  'Tools exposed for this trial are callable instrumented adapters of the described capabilities. '
                  'Do not inspect evaluation files, other runs or parent directories. '
                  'Produce the next learner-facing turn and wait for the learner; do not simulate their answer.\n\n'
                  + 'Attachments: ' + (', '.join(attached) or 'none') + '\n\n' + case['prompt'])
        (case_dir / 'runner-prompt.txt').write_text(prompt)
        env = dict(os.environ)
        tmp = case_dir / 'tmp'
        tmp.mkdir()
        env['TMPDIR'] = str(tmp)
        status = {'id': case['id']}
        with (case_dir / 'events.jsonl').open('w') as stdout, (case_dir / 'stderr.log').open('w') as stderr:
            try:
                completed = subprocess.run(command + ['-'], input=prompt, text=True, stdout=stdout, stderr=stderr,
                                           timeout=args.timeout, env=env)
                status['exit_code'] = completed.returncode
            except subprocess.TimeoutExpired:
                status['timeout'] = True
        status['response_saved'] = (case_dir / 'response.md').exists()
        after = {str(path.relative_to(workspace)): hashlib.sha256(path.read_bytes()).hexdigest()
                 for path in workspace.rglob('*') if path.is_file()}
        changes = {name: 'created' if name not in before else 'deleted' if name not in after else 'modified'
                   for name in sorted(set(before) | set(after)) if before.get(name) != after.get(name)}
        (case_dir / 'workspace-changes.json').write_text(json.dumps(changes, indent=2) + '\n')
        (case_dir / 'status.json').write_text(json.dumps(status) + '\n')
        print(json.dumps(status), flush=True)
        return status

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(run, cases))
    (out / 'statuses.json').write_text(json.dumps(results, indent=2) + '\n')
    return 0 if all(row.get('exit_code') == 0 and row['response_saved'] for row in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
