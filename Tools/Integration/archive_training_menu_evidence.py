"""Archive actual successful menu evidence, preserving original bytes and hashes."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2];src=ROOT/'Saved/Diagnostics/Integration';dst=ROOT/'Docs/Integration/Evidence/TrainingMenu-20261031';dst.mkdir(exist_ok=True)
items=[(src/'training-menu-validation.json','training-menu-validation.json'),(src/'demo-help-validation.json','demo-help-validation.json'),(src/'standalone-menu-v6-60/manifest.json','standalone-menu-v6-60-manifest.json'),(src/'standalone-menu-v5-30/manifest.json','standalone-menu-v5-30-manifest.json'),(src/'standalone-menu-v6-60/00005.png','menu-1280x720.png'),(src/'standalone-menu-v6-60/00067.png','combat-without-demo-help.png')]
rows=[]
for source,name in items:
 target=dst/name;shutil.copy2(source,target);rows.append({'source':str(source.relative_to(ROOT)),'archive':name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
logs={}
for name in ['K02-Standalone-Menu-v5-30.log','K02-Standalone-Menu-v6-60.log']:
 lines=(ROOT/'Saved/Logs'/name).read_text(errors='replace').splitlines();logs[name]={'errors':[x for x in lines if 'Error:' in x or 'Accessed None' in x],'warnings':[x for x in lines if 'Warning:' in x],'map_loads':[x for x in lines if 'LogLoad: Took' in x]}
(dst/'standalone-log-review.json').write_text(json.dumps(logs,indent=2));(dst/'manifest.json').write_text(json.dumps(rows,indent=2));print(dst)
