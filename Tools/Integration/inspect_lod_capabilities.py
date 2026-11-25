"""Read-only LOD API and current own meshes; safe during gameplay inspection."""
import unreal,json
from pathlib import Path
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(),'Stop PIE before Editor asset inspection'
for cls in [unreal.SkeletalMeshEditorSubsystem,unreal.SkeletalMeshLODInfo,unreal.SkeletalMeshOptimizationSettings]:
 print(cls.__name__,cls.__doc__)
sub=unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
for n in dir(sub):
 if any(q in n for q in ['lod','vertex','section','triangle']):print(n,getattr(sub,n).__doc__)
rows=[]
for report in ['protagonist-import.json','roster-import.json']:
 for r in json.loads((Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration'/report).read_text()):
  mesh=unreal.EditorAssetLibrary.load_asset(r['asset']);rows.append({'asset':r['asset'],'lod_count':sub.get_lod_count(mesh),'lod_info':unreal.ToolsetLibrary.get_object_properties(mesh,['LODInfo'])})
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/lod-inventory.json').write_text(json.dumps(rows,indent=2));print('MESHES',len(rows))
