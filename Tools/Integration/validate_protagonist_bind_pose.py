"""UE component-space reference points vs verified Blender derivative physical pose."""
import unreal,json,math
from pathlib import Path
from editor_toolset.toolsets.skeletal_mesh import SkeletalMeshTools as S
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
ROOT=Path(unreal.Paths.project_dir());manifest=json.loads((ROOT/'Saved/Diagnostics/Integration/protagonist-import.json').read_text());rows=[]
for entry in manifest:
 mesh=unreal.load_asset(entry['asset']);base='/Game/K02/Characters/Protagonist/Dogi_v001'
 rig=unreal.load_asset(base+'/Rig/IK_'+entry['id']);rc=unreal.IKRigController.get_controller(rig);old=rc.get_skeletal_mesh()
 assert rc.set_skeletal_mesh(mesh)
 data=json.loads((ROOT/'Saved/Diagnostics/Integration/Protagonist'/(Path(entry['derived_source']).stem+'.json')).read_text())
 bones={}
 for bone,v in data['reference_pose'].items():
  x,y,z=v['position_m'];expected=unreal.Vector(y*100,x*100,z*100)
  actual=rc.get_ref_pose_transform_of_bone(bone)
  bones[bone]={'expected_cm':expected.to_tuple(),'actual_cm':actual.translation.to_tuple(),'error_cm':actual.translation.distance(expected),'scale':actual.scale3d.to_tuple()}
 err=max(b['error_cm'] for b in bones.values());sc=max(max(abs(s-1) for s in b['scale']) for b in bones.values())
 rows.append({'asset':entry['asset'],'max_position_error_cm':err,'max_scale_error':sc,'unweighted_vertices':sum(v['unweighted_vertices'] for v in data['meshes'].values()),'pass':err<.001 and sc<.0001,'bones':bones})
 assert rc.set_skeletal_mesh(old)
 assert unreal.EditorAssetLibrary.save_loaded_asset(rig,False)
(ROOT/'Saved/Diagnostics/Integration/protagonist-bind-poses.json').write_text(json.dumps({'pass':all(r['pass'] for r in rows),'rows':rows},indent=2))
print([(r['asset'].rsplit('/',1)[-1],r['pass'],r['max_position_error_cm']) for r in rows])
