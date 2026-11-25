"""Blender batch: immutable delivery sources -> verified UE centimeter derivatives."""
import sys,json,traceback,hashlib
from pathlib import Path
ROOT=Path('A:/K-02 5.8');PKG=Path('A:/K-02-ArtLab/char_design/Deliveries/Figurinos-UE5-v001')
OUT=ROOT/'Saved/Diagnostics/Integration/Derivatives';OUT.mkdir(exist_ok=True)
normalize=ROOT/'Tools/Integration/normalize_fbx_units.py';verify=ROOT/'Tools/Integration/verify_fbx_derivative.py'
rows=[]
for src in sorted(PKG.glob('*/Exports/*.fbx')):
 ident=src.parent.parent.name;dst=PKG/'UE5_Derived_v002'/ident/src.name;report=OUT/(src.stem+'.json')
 try:
  meta=dst.with_suffix('.json')
  valid=dst.exists() and meta.exists() and json.loads(meta.read_text())['source_sha256']==hashlib.sha256(src.read_bytes()).hexdigest()
  if not valid:
   sys.argv=[str(normalize),'--',str(src),str(dst)];exec(compile(normalize.read_text(),str(normalize),'exec'),{'__name__':'__main__','__file__':str(normalize)})
  sys.argv=[str(verify),'--',str(src),str(dst),str(report)];exec(compile(verify.read_text(),str(verify),'exec'),{'__name__':'__main__','__file__':str(verify)})
  rows.append({'id':ident,'source':str(src),'derivative':str(dst),'validation':str(report),'pass':True})
 except Exception:rows.append({'id':ident,'source':str(src),'pass':False,'error':traceback.format_exc()})
 (OUT/'batch.json').write_text(json.dumps({'pass':all(r['pass'] for r in rows),'complete':len(rows)==18,'rows':rows},indent=2))
print('K02_DERIVATIVES',len(rows),'passed',sum(r['pass'] for r in rows))
