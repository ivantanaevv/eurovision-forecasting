"""Execute the data notebook from a clone, without a Jupyter server."""
from pathlib import Path
import json
import os
from IPython.core.interactiveshell import InteractiveShell

root = Path(__file__).resolve().parents[1]
os.chdir(root)
notebook = json.loads((root / 'notebooks/01_rebuild_dataset.ipynb').read_text())
shell = InteractiveShell.instance()
for index, cell in enumerate(notebook['cells']):
    if cell['cell_type'] != 'code':
        continue
    print(f'Executing data cell {index}', flush=True)
    result = shell.run_cell(''.join(cell['source']), store_history=False)
    if result.error_before_exec or result.error_in_exec:
        raise RuntimeError(f'Data notebook failed in cell {index}') from (
            result.error_before_exec or result.error_in_exec)
print('Verified dataset: build/data/eurovision_features.xlsx')
