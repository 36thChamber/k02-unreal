import bpy,json,sys
from pathlib import Path
ROOT=Path('A:/K-02 5.8');PKG=Path('A:/K-02-ArtLab/char_design/Deliveries/Figurinos-UE5-v001')
s=ROOT/'Tools/Integration/blender_inventory.py';manifest=json.loads((PKG/'manifest.json').read_text())
for c in manifest['characters']:
 result=None
 for i,rel in enumerate([c['editable_blend']]+c.get('additional_blends',[])):
  bpy.ops.wm.open_mainfile(filepath=str(PKG/rel));out=ROOT/'Saved/Diagnostics/Integration'/(c['id']+'-source-part'+str(i)+'.json')
  sys.argv=[str(s),'--',str(out)];exec(compile(s.read_text(),str(s),'exec'),{'__name__':'__main__','__file__':str(s)})
  row=json.loads(out.read_text())
  if result is None:result=row
  else:
   result['materials'].update(row['materials']);result['meshes'].update(row['meshes'])
 result['sources']=[c['editable_blend']]+c.get('additional_blends',[])
 (ROOT/'Saved/Diagnostics/Integration'/(c['id']+'-source.json')).write_text(json.dumps(result,indent=2))
