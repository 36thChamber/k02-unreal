"""Own B1 pilot physics; source sockets are only inspected, never changed."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.skeletal_mesh import SkeletalMeshTools as S
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
BASE='/Game/K02/Validation/ImportProbeV3/B_1'
mesh=unreal.load_asset(BASE+'/Meshes/SK_B_1_Combined_v009')
src=unreal.load_asset('/Game/MACS/Demo/ThirdPersonTemplateUE5/Characters/Mannequins/Meshes/SKM_Manny')
p=unreal.get_default_object(unreal.load_class(None,'/Script/PhysicsToolsets.PhysicsAssetToolset'))
pa=mesh.get_editor_property('physics_asset')
if not pa:pa=p.call_method('CreateFromMesh',args=(mesh.get_path_name().split('.')[0],True))
assert pa
r={'physics':pa.get_path_name(),'bodies':{},'sockets':{},'target_pose':{}}
for name in p.call_method('GetBodyNames',args=(pa,)):
 r['bodies'][name]=[{'name':s.shape_name,'type':str(s.shape_type),'center':s.center.to_tuple(),'radius':s.radius,'length':s.length,'rotation':str(s.rotation),'extent':[s.extent_x,s.extent_y,s.extent_z]} for s in p.call_method('GetBodyShapes',args=(pa,name))]
for name in S.get_socket_names(src):
 so=src.find_socket(name)
 r['sockets'][str(name)]={k:str(so.get_editor_property(k)) for k in ['bone_name','relative_location','relative_rotation','relative_scale']}
rc=unreal.IKRigController.get_controller(unreal.load_asset(BASE+'/Rig/IK_B_1'))
for b in S.get_bone_names(mesh):
 t=rc.get_ref_pose_transform_of_bone(b);r['target_pose'][str(b)]={'translation':t.translation.to_tuple(),'rotation':str(t.rotation),'scale':t.scale3d.to_tuple()}
unreal.EditorAssetLibrary.save_loaded_asset(pa,False);unreal.EditorAssetLibrary.save_loaded_asset(mesh,False)
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/pilot-contact-setup.json').write_text(json.dumps(r,indent=2))
print('Generated pilot physics',r['physics'],'bodies',list(r['bodies']))
