"""Validate the 6 original acute exports and reproduce every aggregate analysis.

Run from any working directory: python /path/to/project/run_all.py
Inputs must be in the project's raw/ directory. No inputs are edited.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

import openpyxl

ROOT = Path(__file__).resolve().parent
SCRIPTS = [
    'analyze_acute_exports.py',
    'analyze_acute_extensions.py',
    'export_summary_tables.py',
    ['standardize_pccl.py', '--cohort', 'acute'],
    ['analyze_principal_diagnosis_sensitivity.py', '--cohort', 'acute'],
    ['analyze_functional_sensitivity.py', '--cohort', 'acute'],
    ['export_severity_tables.py', '--cohort', 'acute'],
]


def validate_inputs(allow_hash_mismatch=False):
    manifest = json.loads((ROOT / 'query_manifest.json').read_text(encoding='utf-8'))
    errors, warnings = [], []
    for item in manifest['exports']:
        path = ROOT / 'raw' / item['filename']
        if not path.is_file():
            errors.append('Missing raw/' + item['filename'])
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != item['sha256']:
            message = 'SHA-256 differs for raw/' + item['filename']
            (warnings if allow_hash_mismatch else errors).append(message)
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        try:
            info = wb['Info']
            checks = {'selection': info['A2'].value,
                      'delivery': info['A5'].value, 'n': int(info['B8'].value)}
            for key, value in checks.items():
                if value != item[key]:
                    errors.append(f'{item["filename"]}: {key} differs from manifest')
        finally:
            wb.close()
    for warning in warnings:
        print('WARNING:', warning)
    if errors:
        raise SystemExit('Input validation failed:\n' + '\n'.join(errors))
    print(f'Validated {len(manifest["exports"])} exports; input workbooks remain unchanged.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-inputs', action='store_true',
                        help='Only validate all files, selections, deliveries, counts and hashes.')
    parser.add_argument('--allow-hash-mismatch', action='store_true',
                        help='Explicitly permit changed file bytes; exact stored metadata and N still required.')
    parser.add_argument('--twofactor', action='store_true',
                        help='Also calculate separate age-by-PCCL and age-by-sex mortality analyses; all 8 all-HD age exports are required.')
    parser.add_argument('--joint', action='store_true',
                        help='Also calculate joint mortality standardization; all 24 new exports are required.')
    args = parser.parse_args()
    validate_inputs(args.allow_hash_mismatch)
    if args.check_inputs:
        return
    result_dir = ROOT / 'results'
    result_dir.mkdir(exist_ok=True)
    commands = list(SCRIPTS)
    commands.append(['analyze_joint_twofactor.py', '--cohort', 'acute'] +
                    ([] if (args.twofactor or args.joint) else ['--status-only']))
    commands.append(['analyze_joint_standardization.py', '--cohort', 'acute'] +
                    ([] if args.joint else ['--status-only']))
    if args.twofactor or args.joint:
        commands.append(['verify_joint_actual.py', '--cohort', 'acute', '--twofactor'])
        if args.joint:
            commands.append(['verify_joint_actual.py', '--cohort', 'acute'])
            commands.append(['analyze_joint_influence.py', '--cohort', 'acute'])
        commands.append(['export_joint_tables.py', '--cohort', 'acute',
                         '--analysis', 'both' if args.joint else 'twofactor'])
    for entry in commands:
        command = [entry] if isinstance(entry, str) else entry
        name = command[0]
        print('Running', ' '.join(command), flush=True)
        log = result_dir / (Path(name).stem + '.log')
        with log.open('w', encoding='utf-8') as stream:
            done = subprocess.run([sys.executable, str(ROOT / name), *command[1:]], cwd=ROOT,
                                  stdout=stream, stderr=subprocess.STDOUT, check=False)
        if done.returncode:
            raise SystemExit(f'{name} failed (exit {done.returncode}); see results/{log.name}')
    print('Completed: results/ contains JSON, curated CSV tables and execution logs; parsed/ contains local full tables.')


if __name__ == '__main__':
    main()
