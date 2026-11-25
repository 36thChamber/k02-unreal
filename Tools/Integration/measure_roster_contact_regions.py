"""Measure preserved full skin bodies; masks/clothes excluded from hit regions."""
import bpy,json,hashlib
from pathlib import Path
ROOT=Path('A:/K-02 5.8');PKG=Path('A:/K-02-ArtLab/char_design/Deliveries/Figurinos-UE5-v001')
base=(ROOT/'Tools/Integration/measure_contact_regions.py').read_text()
for entry in json.loads((PKG/'manifest.json').read_text())['characters']:
 ident=entry['id'];src=PKG/entry['editable_blend'];before=hashlib.sha256(src.read_bytes()).hexdigest()
 s=base.replace("src=ART/'A_Definitive/K02_Skeletal.fbx'",'src=Path('+repr(str(src))+')')
 s=s.replace("bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(src),use_anim=False,automatic_bone_orientation=False)","bpy.ops.wm.open_mainfile(filepath=str(src))")
 s=s.replace("if o.type!='MESH':continue", "if o.type!='MESH' or o.name!="+repr(ident+'_Body')+":continue")
 s=s.replace('Protagonist/contact-regions.json',ident+'-contact-regions.json')
 exec(compile(s,'measure_contact_regions.py','exec'),{'__name__':'__main__'})
 assert before==hashlib.sha256(src.read_bytes()).hexdigest()
print('Five preserved full bodies measured without modifying sources')
