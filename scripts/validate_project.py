"""Cheap syntax checks, including Python embedded in workflow heredocs."""

import ast
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

import yaml


root = Path(__file__).resolve().parents[1]
for path in sorted(root.joinpath('.github/workflows').glob('*.yml')):
    workflow = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
    if not workflow.get('jobs') or not workflow.get('on'):
        raise SystemExit(f'{path}: missing jobs or triggers')
    for job in workflow['jobs'].values():
        for step in job.get('steps', []):
            source = step.get('run')
            if not source:
                continue
            # GitHub expressions are substituted before the runner invokes bash.
            shell = re.sub(r'\$\{\{.*?\}\}', 'validation-value', source)
            subprocess.run(['bash', '-n'], input=shell, text=True, check=True)
            for match in re.finditer(r"<<'PY'\n(.*?)^PY$", source, re.M | re.S):
                ast.parse(match[1], filename=f'{path}:{step["name"]}')
    print(f'{path.relative_to(root)}: YAML, bash, embedded Python OK')
for directory in ('skin', 'addons'):
    for path in root.joinpath(directory).rglob('*.xml'):
        ET.parse(path)
for directory in ('scripts', 'addons'):
    for path in root.joinpath(directory).rglob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
print('Project XML and Python OK; runtime installation not tested.')
