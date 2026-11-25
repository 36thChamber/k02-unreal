"""Apply validated conservative LOD recipe to own imported presentation meshes only."""
import unreal,json,traceback
from pathlib import Path
from editor_toolset.toolsets.skeletal_mesh import SkeletalMeshTools as S
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
ROOT=Path(unreal.Paths.project_dir());A=unreal.EditorAssetLibrary;sub=unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
preset='/Game/K02/Characters/Common/LOD/LOD_K02_Conservative_v001';assert not A.does_asset_exist(preset)
settings=A.duplicate_asset('/Game/K02/Validation/LOD/LOD_K02_Conservative_v001',preset);assert settings;assert A.save_loaded_asset(settings,False)
rows=[];out=ROOT/'Saved/Diagnostics/Integration/character-lods-build.json'
def identity(mesh):
 return {'skeleton':str(mesh.get_editor_property('skeleton').get_path_name()),'physics':str(mesh.get_editor_property('physics_asset').get_path_name()) if mesh.get_editor_property('physics_asset') else None,'materials':[str(m.get_editor_property('material_interface').get_path_name()) for m in mesh.get_editor_property('materials')],'import_sources':str(mesh.get_editor_property('asset_import_data').extract_filenames()),'lod0_vertices':S.get_vertex_count(mesh,0)}
try:
 for report in ['protagonist-import.json','roster-import.json']:
  for item in json.loads((ROOT/'Saved/Diagnostics/Integration'/report).read_text()):
   asset=item['asset']
   if '/Sources/' in asset:continue
   assert asset.startswith('/Game/K02/Characters/');mesh=A.load_asset(asset);assert mesh and sub.get_lod_count(mesh)==1,asset
   before=identity(mesh);mesh.set_editor_property('lod_settings',settings);assert sub.regenerate_lod(mesh,3,False,False)
   after=identity(mesh);assert before==after,(asset,before,after)
   counts=[S.get_vertex_count(mesh,i) for i in range(3)];assert 0<counts[2]<=counts[1]<counts[0],counts
   assert A.save_loaded_asset(mesh,False);rows.append({'asset':asset,'lod_vertices':counts,'identity':after,'identity_preserved':True});out.write_text(json.dumps({'complete':False,'rows':rows},indent=2))
 out.write_text(json.dumps({'complete':True,'rows':rows,'preset':preset},indent=2));print('CHARACTER_LODS_BUILT',len(rows))
except Exception:
 out.write_text(json.dumps({'complete':False,'rows':rows,'error':traceback.format_exc()},indent=2));raise
