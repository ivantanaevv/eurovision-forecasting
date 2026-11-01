"""Check frozen sources, notebook structure and saved 2025 market scores."""
from pathlib import Path
import ast
import csv
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]
sources = ROOT / 'data/sources'
manifest = json.loads((sources / 'reproduction_manifest.json').read_text())
for item in manifest['files']:
    path = (sources / item['file']).resolve()
    assert path.is_relative_to(sources.resolve())
    raw = path.read_bytes()
    assert len(raw) == item['bytes'], item['file']
    assert hashlib.sha256(raw).hexdigest() == item['sha256'], item['file']
for path in list((ROOT / 'notebooks').glob('*.ipynb')) + list((ROOT / 'results').rglob('*.ipynb')):
    nb = json.loads(path.read_text())
    assert nb['nbformat'] == 4 and nb['cells'], path
    for cell in nb['cells']:
        if cell['cell_type'] != 'code':
            continue
        code = ''.join(cell['source'])
        if code.startswith('%%writefile'):
            code = code.split('\n', 1)[1]
        code = '\n'.join(line for line in code.splitlines() if not line.lstrip().startswith(('%', '!')))
        ast.parse(code, filename=str(path))

def read(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))

for task in 'abc':
    folder = ROOT / f'results/task_{task}/market'
    forecasts = read(folder / 'comparison_2025.csv')
    metrics = read(folder / 'metrics_2025.csv')
    for model in metrics:
        rows = [r for r in forecasts if r['model'] == model['model']]
        if task == 'c':
            calculated = {key: sum(float(r[key]) for r in rows)/len(rows)
                          for key in ['brier', 'log_loss', 'accuracy', 'top3_accuracy']}
        else:
            prob = 'p_top10' if task == 'a' else 'p'
            target = 'target_top10' if task == 'a' else 'target_audience_above_jury'
            p = [min(1-1e-12, max(1e-12, float(r[prob]))) for r in rows]
            y = [int(r[target]) for r in rows]
            calculated = {'brier': sum((a-b)**2 for a,b in zip(p,y))/len(rows),
                'binary_log_loss' if task == 'a' else 'log_loss':
                -sum(b*math.log(a)+(1-b)*math.log1p(-a) for a,b in zip(p,y))/len(rows)}
        for key,value in calculated.items():
            assert math.isclose(value,float(model[key]),rel_tol=1e-8,abs_tol=1e-8),(task,model['model'],key)
print(f'OK: {len(manifest["files"])} source hashes; notebook syntax; all 2025 market scores.')
